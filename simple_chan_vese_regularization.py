#!/usr/bin/python
import argparse
import os
from tulip import *

def perform_chanvese_regularization(data_image, seed_image, lambda1, lambda2, iter, output, export_interval = 0):
    ds = tlp.getDefaultPluginParameters('Import image')
    ds['file::File']                               =  data_image
    ds['Neighborhood type'].setCurrent('Circular')
    ds['Neighborhood radius']                      =  1
    ds['Positionning']                             =  False
    ds['Spacing']                                  =  1
    ds['Property type'].setCurrent('DoubleVector')
    ds['Property name']                            =  'data'
    ds['Convert to grayscale']                     =  False
    g = tlp.importGraph('Import image', ds)

    print 'Image imported'

    data = g.getDoubleVectorProperty('data')
    n = g.getOneNode()

    seed_tmp_prop = g.getBooleanProperty('seed_tmp')

    ds = tlp.getDefaultPluginParameters('Load image data', g)
    ds['file::Image'] = seed_image
    ds['Property']    = seed_tmp_prop
    result, error = g.applyAlgorithm('Load image data', ds)

    if result == False:
        print error
    print 'Seed imported'

    seed_prop = g.getDoubleProperty('seed')
    seed_prop.setAllNodeValue(0.0)
    for n in g.getNodes():
        if seed_tmp_prop.getNodeValue(n):
            seed_prop.setNodeValue(n, 1.0)

    g.delLocalProperty('seed_tmp')

    similarity = g.getDoubleProperty('similarity')
    similarity.setAllEdgeValue(1.0)

    result_prop = g.getDoubleProperty('result')
    segmentation_result_prop = g.getBooleanProperty('segmentation_result')

    ds = tlp.getDefaultPluginParameters('ChanVese Regularization', g)
    ds['seed']                  = seed_prop
    ds['result']                = result_prop
    ds['segmentation result']   = segmentation_result_prop
    ds['data']                  = data
    ds['similarity measure']    = similarity
    ds['number of iterations']  = iter
    ds['lambda1']               = lambda1
    ds['lambda2']               = lambda2
    ds['export interval']       = export_interval
    ds['dir::export directory'] = os.path.dirname(os.path.realpath(output))
    result, error = g.applyAlgorithm('ChanVese Regularization', ds)

    if result == False:
        print error
    print 'ChanVese regularization successfully applied'

    path, pattern = os.path.split(os.path.realpath(output))

    ds = tlp.getDefaultPluginParameters('Export image', g)
    ds['Property']              = segmentation_result_prop
    ds['dir::Export directory'] = path
    ds['Export pattern']        = pattern
    result, error = g.applyAlgorithm('Export image', ds)

    if result == False:
        print error
    print 'Segmentation exported'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Apply the Chan & Vese graph regularization algorithm on an image',
            epilog='Add <tulip install dir>/lib/python to the PYTHONPATH environment variable, and <tulip install dir>/lib to the LD_LIBRARY_PATH one.')
    parser.add_argument('--image', '-i', metavar='file', help='the image to process', required = True)
    parser.add_argument('--seed', '-s', metavar='file', help='the seed used by the regularization algorithm', required = True)
    parser.add_argument('--iter', metavar='N', type=int, nargs = '?', default = 100, help='the number of iterations to perform')
    parser.add_argument('--lambda1', metavar='N', type=float, nargs = '?', default = 1)
    parser.add_argument('--lambda2', metavar='N', type=float, nargs = '?', default = 1)
    parser.add_argument('--output', '-o', metavar='file', help='where the segmentation result will be saved', required = True)
    parser.add_argument('--export-interval', metavar='N', type=int, nargs = '?', default = 0)
    args = parser.parse_args()

    perform_chanvese_regularization(args.image, args.seed, args.lambda1, args.lambda2, args.iter, args.output, args.export_interval)
