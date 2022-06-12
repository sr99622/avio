#define NO_IMPORT_ARRAY
#include "numpy_init.h"
#include "PyRunner.h"

namespace avio
{

PyRunner::PyRunner(const std::string& dir, const std::string& file, const std::string& py_class, 
	const std::string& arg)
{
	std::cout << "python_dir: " << dir << std::endl;
	std::cout << "python_file: " << file << std::endl;
	std::cout << "python_class: " << py_class << std::endl;
	std::cout << "init arg: " << arg << std::endl;

	try {
		CPyObject sysPath = PySys_GetObject("path");
		CPyObject dirName = PyUnicode_FromString(dir.c_str());
		PyList_Append(sysPath, dirName);

		CPyObject pName = PyUnicode_FromString(file.c_str());		     if (!pName)   throw Exception("pName");
		CPyObject pModule = PyImport_Import(pName);                      if (!pModule) throw Exception("pModule");
		CPyObject pDict = PyModule_GetDict(pModule);                     if (!pDict)   throw Exception("pDict");
		CPyObject pItem = PyDict_GetItemString(pDict, py_class.c_str()); if (!pItem)   throw Exception("pItem");

		CPyObject pWrap = NULL;
		CPyObject pArg = NULL;

		if (arg.length() > 0) {
			pArg = Py_BuildValue("(s)", arg.c_str());
			pWrap = PyTuple_New(1);
			PyTuple_SetItem(pWrap, 0, pArg);
		}

		pClass = PyObject_CallObject(pItem, pWrap);                      if (!pClass) throw Exception("pClass");
		std::cout << "PyRunner construction complete" << std::endl;
	}
	catch (const Exception& e) {
		std::cout << "PyRunner constuctor exception: " << e.what() << std::endl;
		std::exit(0);
	}
}

CPyObject PyRunner::getImage(const cv::Mat& image)
{
	CPyObject result;
	try {
		if (!PyArray_API) throw Exception("numpy not initialized");
		npy_intp dimensions[3] = { image.rows, image.cols, image.channels() };
		pData = PyArray_SimpleNewFromData(3, dimensions, NPY_UINT8, image.data);
		if (!pData) throw Exception("pData");
		result = Py_BuildValue("(O)", pData);
	}
	catch (const Exception& e) {
		ex.msg(e.what(), MsgPriority::CRITICAL, "PyRunner::getImage exception: ");
	}
	return result;
}

bool PyRunner::run(Frame& f, const std::string& events)
{
	bool result = false;
	if (f.isValid()) {
		CPyObject pImage = getImage(f.mat());
		CPyObject pRTS = Py_BuildValue("(i)", f.m_rts);

		// pts is long long so use stream writer to convert
		std::stringstream str;
		str << f.m_frame->pts;
		CPyObject pStrPTS = Py_BuildValue("(s)", str.str().c_str());

		CPyObject pEvents = Py_BuildValue("(s)", events.c_str());

		CPyObject pArg = PyTuple_New(4);
		PyTuple_SetItem(pArg, 0, pImage);
		PyTuple_SetItem(pArg, 1, pStrPTS);
		PyTuple_SetItem(pArg, 2, pRTS);
		PyTuple_SetItem(pArg, 3, pEvents);

		CPyObject pWrap = PyTuple_New(1);
		PyTuple_SetItem(pWrap, 0, pArg);

		PyObject* pValue = PyObject_CallObject(pClass, pWrap);
		if (pValue) {
			if (pValue != Py_None) {
				PyObject* pImgRet = NULL;
				PyObject* pPtsRet = NULL;
				PyObject* pRecRet = NULL;
				if (PyTuple_Check(pValue)) {
					Py_ssize_t size = PyTuple_GET_SIZE(pValue);
					if (size > 0) pImgRet = PyTuple_GetItem(pValue, 0);
					if (size == 2) {
						PyObject* tmp = PyTuple_GetItem(pValue, 1);
						if (PyBool_Check(tmp))
							pRecRet = tmp;
						else
							pPtsRet = tmp;
					}
					if (size == 3) {
						pPtsRet = PyTuple_GetItem(pValue, 1);
						pRecRet = PyTuple_GetItem(pValue, 2);
					}
				}
				else if (PyArray_Check(pValue)) {
					pImgRet = pValue;
				}
				else {
					if (PyBool_Check(pValue))
						pRecRet = pValue;
					else
						pPtsRet = pValue;
				}

				if (pImgRet) {
					if (PyArray_Check(pImgRet)) {
						int ndims = PyArray_NDIM((const PyArrayObject*)pImgRet);
						const npy_intp* np_sizes = PyArray_DIMS((PyArrayObject*)pImgRet);
						const npy_intp* np_strides = PyArray_STRIDES((PyArrayObject*)pImgRet);

						int height = np_sizes[0];
						int width = np_sizes[1];
						int depth = np_sizes[2];
						int stride = np_strides[0];

						int buf_size = height * width * depth;
						uint8_t* buffer = new uint8_t[buf_size];
						uint8_t* np_buf = (uint8_t*)PyArray_BYTES((PyArrayObject*)pImgRet);

						for (int y = 0; y < height; y++)
							memcpy(buffer + y * width * depth, np_buf + y * stride, width * depth);

						cv::Mat m(np_sizes[0], np_sizes[1], CV_8UC3, buffer);

						int64_t rts = f.m_rts;
						int64_t pts = f.m_frame->pts;
						f = Frame(m);
						f.m_rts = rts;
						f.m_frame->pts = pts;
						delete[] buffer;
					}
				}

				if (pPtsRet) {
					if (pPtsRet != Py_None) {
						PyObject* repr = PyObject_Repr(pPtsRet);
						PyObject* str = PyUnicode_AsEncodedString(repr, "utf-8", "strict");
						char* result = PyBytes_AsString(str);
						std::size_t pos = 0;
						std::string s(result);
						s.erase(std::remove(s.begin(), s.end(), '\''), s.end());
						try {
							int64_t pts = std::stoll(s, &pos);
							f.m_frame->pts = pts;
						}
						catch (const std::exception& e) {
							std::cout << "Error interpreting python pts return value: (" << result << ") " << e.what() << std::endl;
						}
					}
				}

				if (pRecRet) {
					if (pRecRet != Py_None) {
						if (pRecRet == Py_True)
							result = true;
					}
				}
			}

			Py_DECREF(pValue);
			pValue = NULL;

			if (pData) Py_DECREF(pData);
			pData = NULL;
		}
		else {
			std::cout << "Error: pyrunner returned null pvalue" << std::endl;
		}
	}

	return result;
}

}
