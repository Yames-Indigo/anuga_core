#cython: wraparound=False, boundscheck=False, cdivision=True, profile=False, nonecheck=False, overflowcheck=False, cdivision_warnings=False, unraisable_tracebacks=False
import cython
from libc.stdlib cimport malloc, free
# import both numpy and the Cython declarations for numpy
import numpy as np
cimport numpy as np

np.import_array() # avoid segmentation fault

ctypedef double REAL

# declare the interface to the C code
cdef extern from "triangle.c":
    struct triangulateio:
        REAL* pointlist
        REAL* pointattributelist
        int* pointmarkerlist
        int numberofpoints
        int numberofpointattributes
        int* trianglelist
        REAL* triangleattributelist
        REAL* trianglearealist
        int* neighborlist
        int numberoftriangles
        int numberofcorners
        int numberoftriangleattributes
        int* segmentlist
        int* segmentmarkerlist
        int numberofsegments
        REAL* holelist
        int numberofholes
        REAL* regionlist
        int numberofregions
        int* edgelist
        int* edgemarkerlist
        REAL* normlist
        int numberofedges
    void triangulate(char*, triangulateio*, triangulateio*, triangulateio*)

def genMesh(np.ndarray pointlist not None,\
            np.ndarray seglist not None,\
            np.ndarray holelist not None,\
            np.ndarray regionlist not None,\
            np.ndarray pointattributelist not None,\
            np.ndarray segmarkerlist not None,\
            char* mod):

    cdef triangulateio in_t, out_t
    cdef triangulateio in_test

    cdef np.npy_intp* dimensions

    cdef REAL Attr
    cdef int i, j, iatt, n, write_here, N
    cdef int a, b, c
    cdef int marker
    cdef int tuplesize
    cdef int index = 0
    cdef double x,y

    cdef np.ndarray[int, ndim=2, mode="c"] gentrianglelist
    cdef np.ndarray[double, ndim=2, mode="c"] genpointlist
    cdef np.ndarray[int, ndim=1, mode="c"] genpointmarkerlist
    cdef np.ndarray[double, ndim=2, mode="c"] genpointattributelist
    cdef np.ndarray[double, ndim=2, mode="c"] gentriangleattributelist
    cdef np.ndarray[int, ndim=2, mode="c"] gensegmentlist
    cdef np.ndarray[int, ndim=1, mode="c"] gensegmentmarkerlist
    cdef np.ndarray[int, ndim=2, mode="c"] genneighborlist

    in_t.numberofpoints = pointlist.shape[0]
    in_t.pointlist = <double* > pointlist.data
    in_t.pointmarkerlist = <int* >NULL

    in_t.numberofregions = regionlist.shape[0]
    in_t.regionlist = <double* > regionlist.data

    in_t.numberofsegments = seglist.shape[0]
    in_t.segmentlist = <int* > seglist.data
    in_t.segmentmarkerlist = <int* > segmarkerlist.data

    in_t.numberoftriangles = 0
    in_t.trianglelist = <int* >NULL
    in_t.numberoftriangleattributes = 0;
    in_t.triangleattributelist = <REAL* >NULL
    in_t.trianglearealist = <REAL* >NULL
    in_t.neighborlist = <int* >NULL
    in_t.numberofcorners = 0

    in_t.numberofholes = holelist.shape[0]

    if in_t.numberofholes != 0:
        in_t.holelist = <double* > holelist.data
    else:
        in_t.holelist = <REAL* >NULL

    if pointattributelist.shape[0] == 0:
        in_t.numberofpointattributes = 0
        in_t.pointattributelist = <double* >NULL
    else:
        if pointattributelist.shape[1] == 0:
            in_t.numberofpointattributes = 0
            in_t.pointattributelist = <double* >NULL
        else:
            in_t.numberofpointattributes = pointattributelist.shape[1]
            in_t.pointattributelist = <double* > pointattributelist.data

    out_t.pointlist = <REAL* >NULL
    out_t.pointmarkerlist = <int* >NULL
    out_t.pointattributelist = <REAL* >NULL

    out_t.trianglelist = <int* >NULL
    out_t.triangleattributelist = <REAL* >NULL
    out_t.trianglearealist = <REAL* >NULL
    out_t.neighborlist = <int* >NULL

    out_t.segmentlist = <int* >NULL
    out_t.segmentmarkerlist = <int* >NULL

    out_t.edgelist = <int* >NULL
    out_t.edgemarkerlist = <int* >NULL

    out_t.holelist = <REAL* >NULL
    out_t.regionlist = <REAL* >NULL

    triangulate(mod, &in_t, &out_t, <triangulateio* >NULL)

    dimensions = <np.npy_intp* > malloc(2 * sizeof(np.npy_intp))

    dimensions[0] = out_t.numberoftriangles
    dimensions[1] = 3
    gentrianglelist = np.PyArray_SimpleNewFromData(2, dimensions, np.NPY_INT32, out_t.trianglelist)

    dimensions[0] = out_t.numberofpoints
    dimensions[1] = 2
    genpointlist = np.PyArray_SimpleNewFromData(2, dimensions, np.NPY_DOUBLE, out_t.pointlist)

    dimensions[0] = out_t.numberofpoints
    genpointmarkerlist = np.PyArray_SimpleNewFromData(1, dimensions, np.NPY_INT32, out_t.pointmarkerlist)

    dimensions[0] = out_t.numberofpoints
    dimensions[1] = out_t.numberofpointattributes
    genpointattributelist = np.PyArray_SimpleNewFromData(2, dimensions, np.NPY_DOUBLE, out_t.pointattributelist)

    dimensions[0] = out_t.numberoftriangles
    dimensions[1] = out_t.numberoftriangleattributes
    gentriangleattributelist = np.PyArray_SimpleNewFromData(2, dimensions, np.NPY_DOUBLE, out_t.triangleattributelist)

    dimensions[0] = out_t.numberofsegments
    dimensions[1] = 2
    gensegmentlist = np.PyArray_SimpleNewFromData(2, dimensions, np.NPY_INT32, out_t.segmentlist)

    dimensions[0] = out_t.numberofsegments
    gensegmentmarkerlist = np.PyArray_SimpleNewFromData(1, dimensions, np.NPY_INT32, out_t.segmentmarkerlist)

    if out_t.neighborlist != NULL:
        dimensions[0] = out_t.numberoftriangles
        dimensions[1] = 3
        genneighborlist = np.PyArray_SimpleNewFromData(2, dimensions, np.NPY_INT32, out_t.neighborlist)
    else:
        genneighborlist = np.zeros((0,0), dtype=np.int32)

    if not(out_t.trianglearealist):
        free(out_t.trianglearealist)
        out_t.trianglearealist = NULL

    if not(out_t.edgelist):
        free(out_t.edgelist)
        out_t.edgelist = NULL

    if not(out_t.edgemarkerlist):
        free(out_t.edgemarkerlist)
        out_t.edgemarkerlist = NULL

    if not(out_t.holelist):
        free(out_t.holelist)
        out_t.holelist = NULL

    if not(out_t.regionlist):
        free(out_t.regionlist)
        out_t.regionlist = NULL

    free(dimensions)

    return gentrianglelist, genpointlist, genpointmarkerlist, genpointattributelist, gentriangleattributelist, gensegmentlist, gensegmentmarkerlist, genneighborlist