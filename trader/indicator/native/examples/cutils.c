#include <Python.h>
#include <stdio.h>

#define VOID   void
typedef uint8_t      BOOLEAN;
typedef int8_t       INT8;
typedef uint8_t      UINT8;
typedef int16_t      INT16;
typedef uint16_t     UINT16;
typedef int32_t      INT32;
typedef uint32_t     UINT32;
typedef int64_t      INT64;
typedef uint64_t     UINT64;
typedef char         CHAR8;
typedef uint16_t     CHAR16;
typedef size_t       UINTN;

UINT8 calculateSum8(const UINT8* buffer, UINT32 bufferSize)
{
    if (!buffer)
        return 0;

    UINT8 counter = 0;

    while (bufferSize--)
        counter += buffer[bufferSize];

    return counter;
}

UINT8 calculateChecksum8(const UINT8* buffer, UINT32 bufferSize)
{
    if (!buffer)
        return 0;

    return (UINT8)0x100 - calculateSum8(buffer, bufferSize);
}

UINT16 calculateChecksum16(const UINT16* buffer, UINT32 bufferSize)
{
    if (!buffer)
        return 0;

    UINT16 counter = 0;
    UINT32 index = 0;

    bufferSize /= sizeof(UINT16);

    for (; index < bufferSize; index++) {
        counter = (UINT16)(counter + buffer[index]);
    }

    return (UINT16)0x10000 - counter;
}

VOID uint32ToUint24(UINT32 size, UINT8* ffsSize)
{
    ffsSize[2] = (UINT8)((size) >> 16);
    ffsSize[1] = (UINT8)((size) >> 8);
    ffsSize[0] = (UINT8)((size));
}

UINT32 uint24ToUint32(const UINT8* ffsSize)
{
    return (ffsSize[2] << 16) +
        (ffsSize[1] << 8) +
        ffsSize[0];
}

static PyObject * sum8(PyObject * self, PyObject * args)
{
  PyByteArrayObject * input;
  UINT8 *input_data;
  UINT8 result = 0;
  int len=0;
  //PyObject * ret;

  if (!PyArg_ParseTuple(args, "O", &input))
      return NULL;

  len = PyByteArray_Size((PyObject*)input);
  //printf("%s len=%d\n", __FUNCTION__, len);
  input_data = PyByteArray_AsString((PyObject*)input);

  result = calculateSum8(input_data, len);

  return Py_BuildValue("B", result);
}

static PyObject * checksum8(PyObject * self, PyObject * args)
{
  PyByteArrayObject * input;
  UINT8 *input_data;
  UINT8 result = 0;
  int len=0;
  //PyObject * ret;

  if (!PyArg_ParseTuple(args, "O", &input))
      return NULL;

  len = PyByteArray_Size((PyObject*)input);
  //printf("%s len=%d\n", __FUNCTION__, len);
  input_data = PyByteArray_AsString((PyObject*)input);

  result = calculateChecksum8(input_data, len);

  return Py_BuildValue("B", result);
}

static PyMethodDef HelloMethods[] = {
 { "sum8", sum8, METH_VARARGS, "sum8" },
 { "checksum8", checksum8, METH_VARARGS, "checksum8" },
 { NULL, NULL, 0, NULL }
};

DL_EXPORT(void) initcutils(void)
{
  Py_InitModule("cutils", HelloMethods);
}
