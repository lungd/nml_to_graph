#!/usr/bin/python

import os
import sys
import xml.etree.ElementTree as ET

from glob import glob
from subprocess import call


def usage(script):
    print 'USAGE: python %s directory graphviz_filename figure_filename' % (script)
    sys.exit(-1)


def is_muscle(cell):
    return cell.startswith('MV') or cell.startswith('MD')


def get_cells(root):
    cells = []
    #network = root.find('network')
    for cell in root.getiterator():
        if 'population' not in cell.tag:
            continue
        if is_muscle(cell.attrib['id']):
            continue
        cells.append(cell.attrib['id'])
    return cells


def get_elec_conns(root):
    elec_conns = []
    for elec_conn in root.getiterator():
        if 'electricalProjection' not in elec_conn.tag:
            continue
        pre = elec_conn.attrib['presynapticPopulation']
        post = elec_conn.attrib['postsynapticPopulation']

        if is_muscle(pre) or is_muscle(post):
            continue

        elec_conns.append('%s -> %s [minlen=2 arrowhead="tee"]' % (pre, post))
    return elec_conns    


def get_chem_conns(root):
    chem_conns = []
    for chem_conn in root.getiterator():
        if 'continuousProjection' not in chem_conn.tag:
            continue
        pre = chem_conn.attrib['presynapticPopulation']
        post = chem_conn.attrib['postsynapticPopulation']

        if is_muscle(pre) or is_muscle(post):
            continue

        for child in chem_conn:
            if 'inh' in child.attrib['postComponent']:
                chem_conns.append('%s -> %s [minlen=2 color=red]' % (pre, post))
            else:
                chem_conns.append('%s -> %s [minlen=2]' % (pre, post))
    return chem_conns


def write_graph_file(filename, cells, elec_conns, chem_conns):
    with open(filename, 'w') as graph:
        graph.write('digraph exp {\n')
        
        graph.write('node [fontsize=11]; ')
        for cell in cells:
            graph.write('%s; ' % cell)
        graph.write('\n')

        for elec in elec_conns:
            graph.write('%s;\n' % elec)

        for chem in chem_conns:
            graph.write('%s;\n' % chem)

        graph.write('splines=true;')
        graph.write('sep="+25,25";')
        graph.write('overlap=false\n')
        graph.write('fontsize=12;\n')
        graph.write('}')


def find_nml_files(directory='.', recursive=False):
    files = []
    for file in os.listdir(directory):
        if file.endswith(".nml"):
            files.append(os.path.join(directory, file))

    if recursive:
        return [y for x in os.walk(directory) for y in glob(os.path.join(x[0], '*.nml'))]
    
    return files


def execute_graph_generator(graphviz_file, fig_file):
    with open(fig_file, 'w') as fig:
        call(['neato', '-Tpng', graphviz_file], stdout=fig)


def main():

    if len(sys.argv) == 5:
        filenames = find_nml_files(sys.argv[1], recursive=True)
    else:
        filenames = find_nml_files(sys.argv[1])

    print filenames

    for filename in filenames:
        dirname = os.path.dirname(filename)
        tree = ET.parse(filename)
        root = tree.getroot()
        
        cells = get_cells(root)
        elec_conns = get_elec_conns(root)
        chem_conns = get_chem_conns(root)

        write_graph_file(os.path.join(dirname, sys.argv[2]), cells, elec_conns, chem_conns)

        execute_graph_generator(os.path.join(dirname, sys.argv[2]), os.path.join(dirname, sys.argv[3]))
    

if __name__ == '__main__':

    if len(sys.argv) < 4:
        usage(sys.argv[0])

    main()
    
