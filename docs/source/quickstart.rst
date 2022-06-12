Windows Quick Start
===================

.. _quick_start:


The following instructions are for windows users.  

Anaconda should be installed on the host machine.  The download is available at
https://www.anaconda.com/products/distribution#windows.

Using the anaconda prompt, as shown in this link 
https://docs.anaconda.com/anaconda/user-guide/getting-started/#open-anaconda-prompt
create a new conda environment and activate it, as shown below.

.. code-block:: text

    conda create --name test
    conda activate test

Add the conda forge channel to the conda configuration

.. code-block:: text

    conda config --add channels conda-forge

Install avio

.. code-block:: text

    conda install -c sr99622 avio

Download the source code and example programs

.. code-block:: text

    git clone --recursive https://github.com/sr99622/avio.git

Run the sample test program

.. code-block:: text

    cd avio\python
    python test.py
