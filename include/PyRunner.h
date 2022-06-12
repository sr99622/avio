#pragma once

#include <iostream>
#include <Python.h>
#include <opencv2/opencv.hpp>
#include "pyhelper.h"
#include "Queue.h"
#include "Frame.h"
#include "Exception.h"

namespace avio
{

class PyRunner {
public:
	PyRunner() {}
	PyRunner(const std::string& dir, const std::string& file, const std::string& py_class, const std::string& arg);
	CPyObject getImage(const cv::Mat& image);
	bool run(Frame& f, const std::string& events);

	CPyObject pClass = nullptr;
	Queue<Frame>* frame_q = nullptr;
	ExceptionHandler ex;
	bool initialized = false;
	bool loop_back = false;

	PyObject* pData = NULL;

};

}