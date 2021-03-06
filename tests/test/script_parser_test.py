#!/usr/bin/env python
'''module to test the vsc.pbs.script_parser.PbsScriptParser parser'''

import json
import unittest
from vsc.pbs.script_parser import PbsScriptParser


class PbsScriptParserTest(unittest.TestCase):
    '''Tests for the pbsnodes output parser'''

    def setUp(self):
        config_file_name = '../../conf/config.json'
        event_file_name = '../../lib/events.json'
        with open(config_file_name, 'r') as config_file:
            self._config = json.load(config_file)
        with open(event_file_name, 'r') as event_file:
            self._event_defs = json.load(event_file)

    def test_simple(self):
        file_name = 'data/simple.pbs'
        nodes = 2
        ppn = 4
        walltime = 72*3600
        partition = self._config['default_partition']
        parser = PbsScriptParser(self._config, self._event_defs)
        with open(file_name, 'r') as pbs_file:
            parser.parse_file(pbs_file)
        job = parser.job
        nodes_specs = job.resource_specs['nodes'][0]
        self.assertEquals(nodes, nodes_specs['nodes'])
        self.assertEquals(ppn, nodes_specs['ppn'])
        self.assertEquals(walltime, job.resource_specs['walltime'])
        self.assertEquals(partition, job.resource_specs['partition'])

    def test_parsing(self):
        file_name = 'data/correct.pbs'
        name = 'my_job'
        project = 'lp_qlint'
        nodes = 2
        ppn = 4
        walltime = 72*3600
        qos = 'debugging'
        join = 'oe'
        parser = PbsScriptParser(self._config, self._event_defs)
        with open(file_name, 'r') as pbs_file:
            parser.parse_file(pbs_file)
        job = parser.job
        self.assertEquals(name, job.name)
        self.assertEquals(project, job.project)
        nodes_specs = job.resource_specs['nodes'][0]
        self.assertEquals(nodes, nodes_specs['nodes'])
        self.assertEquals(ppn, nodes_specs['ppn'])
        self.assertEquals(walltime, job.resource_specs['walltime'])
        self.assertEquals(qos, job.resource_specs['qos'])
        self.assertEquals(join, job.join)

    def test_size_in_bytes(self):
        file_name = 'data/size_in_bytes.pbs'
        size = 4096
        parser = PbsScriptParser(self._config, self._event_defs)
        with open(file_name, 'r') as pbs_file:
            parser.parse_file(pbs_file)
        job = parser.job
        self.assertEquals(size, job.resource_specs['mem'])

    def test_dos(self):
        file_name = 'data/dos.pbs'
        nr_syntax_events = 4
        event_names = ['dos_format']
        parser = PbsScriptParser(self._config, self._event_defs)
        with open(file_name, 'r') as pbs_file:
            parser.parse_file(pbs_file)
        self.assertEquals(nr_syntax_events, len(parser.events))
        for event in parser.events:
            self.assertTrue(event['id'] in event_names)
        self.assertEquals(nr_syntax_events, parser.nr_errors)

    def test_nodes_ppn_wrong_spec(self):
        file_name = 'data/nodes_ppn_wrong_spec.pbs'
        nr_syntax_events = 1
        event_names = ['ppn_no_number']
        parser = PbsScriptParser(self._config, self._event_defs)
        with open(file_name, 'r') as pbs_file:
            parser.parse_file(pbs_file)
        self.assertEquals(nr_syntax_events, len(parser.events))
        for event in parser.events:
            self.assertTrue(event['id'] in event_names)
        self.assertEquals(nr_syntax_events, parser.nr_errors)

    def test_misplaced_shebang(self):
        file_name = 'data/misplaced_shebang.pbs'
        event_names = ['missing_shebang', 'misplaced_shebang']
        parser = PbsScriptParser(self._config, self._event_defs)
        with open(file_name, 'r') as pbs_file:
            parser.parse_file(pbs_file)
        self.assertEquals(len(event_names), len(parser.events))
        for event in parser.events:
            self.assertTrue(event['id'] in event_names)
        self.assertEquals(len(event_names), parser.nr_warnings)

    def test_indented_pbs_directive(self):
        file_name = 'data/indented_pbs_directive.pbs'
        event_names = ['indented_pbs_dir']
        parser = PbsScriptParser(self._config, self._event_defs)
        with open(file_name, 'r') as pbs_file:
            parser.parse_file(pbs_file)
        self.assertEquals(len(event_names), len(parser.events))
        for event in parser.events:
            self.assertTrue(event['id'] in event_names)
        self.assertEquals(len(event_names), parser.nr_warnings)

    def test_pbs_space_directive(self):
        file_name = 'data/pbs_space_directive.pbs'
        event_names = ['space_in_pbs_dir']
        parser = PbsScriptParser(self._config, self._event_defs)
        with open(file_name, 'r') as pbs_file:
            parser.parse_file(pbs_file)
        self.assertEquals(len(event_names), len(parser.events))
        for event in parser.events:
            self.assertTrue(event['id'] in event_names)
        self.assertEquals(len(event_names), parser.nr_warnings)

    def test_wrong_options(self):
        file_name = 'data/wrong_options.pbs'
        event_names = ['invalid_join', 'invalid_job_name']
        parser = PbsScriptParser(self._config, self._event_defs)
        with open(file_name, 'r') as pbs_file:
            parser.parse_file(pbs_file)
        self.assertEquals(len(event_names), len(parser.events))
        for event in parser.events:
            self.assertTrue(event['id'] in event_names)
        self.assertEquals(len(event_names), parser.nr_errors)

    def test_mem_specs(self):
        file_name = 'data/mem_specs.pbs'
        event_names = ['invalid_mem_format']
        parser = PbsScriptParser(self._config, self._event_defs)
        with open(file_name, 'r') as pbs_file:
            parser.parse_file(pbs_file)
        self.assertEquals(len(event_names), len(parser.events))
        for event in parser.events:
            self.assertTrue(event['id'] in event_names)

    def test_pmem_specs(self):
        file_name = 'data/pmem_specs.pbs'
        event_names = ['invalid_pmem_format']
        parser = PbsScriptParser(self._config, self._event_defs)
        with open(file_name, 'r') as pbs_file:
            parser.parse_file(pbs_file)
        self.assertEquals(len(event_names), len(parser.events))
        for event in parser.events:
            self.assertTrue(event['id'] in event_names)
        self.assertEquals(len(event_names), parser.nr_errors)

    def test_multiple_resources(self):
        file_name = 'data/multiple_resources.pbs'
        nr_specs = 2
        nr_nodes = [3, 5]
        features = ['mem128', 'mem64']
        nr_features = 1
        parser = PbsScriptParser(self._config, self._event_defs)
        with open(file_name, 'r') as pbs_file:
            parser.parse_file(pbs_file)
        job = parser.job
        node_specs = job.resource_specs['nodes']
        self.assertEquals(nr_specs, len(node_specs))
        for i, node_spec in enumerate(node_specs):
            self.assertEquals(nr_nodes[i], node_spec['nodes'])
            self.assertEquals(nr_features, len(node_spec['properties']))
            self.assertEquals(features[i], node_spec['properties'][0])

    def test_malformed_pbs_directive(self):
        file_name = 'data/malformed_pbs_directive.pbs'
        event_names = ['malformed_pbs_dir']
        parser = PbsScriptParser(self._config, self._event_defs)
        with open(file_name, 'r') as pbs_file:
            parser.parse_file(pbs_file)
        self.assertEquals(len(event_names), len(parser.events))
        for event in parser.events:
            self.assertTrue(event['id'] in event_names)
        self.assertEquals(len(event_names), parser.nr_errors)

    def test_missing_l_resource(self):
        file_name = 'data/missing_l_resource.pbs'
        event_names = []
        parser = PbsScriptParser(self._config, self._event_defs)
        with open(file_name, 'r') as pbs_file:
            parser.parse_file(pbs_file)
        self.assertEquals(len(event_names), len(parser.events))

    def test_confused_mail_options(self):
        file_name = 'data/confused_mail_options.pbs'
        event_names = ['invalid_mail_address']
        parser = PbsScriptParser(self._config, self._event_defs)
        with open(file_name, 'r') as pbs_file:
            parser.parse_file(pbs_file)
        self.assertEquals(len(event_names), len(parser.events))
        for event in parser.events:
            self.assertTrue(event['id'] in event_names)
        self.assertEquals(len(event_names), parser.nr_warnings)

    def test_correct_start_date_time(self):
        file_name = 'data/correct_start_datetime.pbs'
        event_names = []
        parser = PbsScriptParser(self._config, self._event_defs)
        with open(file_name, 'r') as pbs_file:
            parser.parse_file(pbs_file)
        self.assertEquals(len(event_names), len(parser.events))

    def test_invalid_start_date_time(self):
        file_name = 'data/invalid_start_datetime.pbs'
        event_names = ['invalid_datetime']
        parser = PbsScriptParser(self._config, self._event_defs)
        with open(file_name, 'r') as pbs_file:
            parser.parse_file(pbs_file)
        self.assertEquals(len(event_names), len(parser.events))
        for event in parser.events:
            self.assertTrue(event['id'] in event_names)
        self.assertEquals(len(event_names), parser.nr_errors)

    def test_no_dash_options(self):
        file_name = 'data/no_dash_option.pbs'
        event_names = ['malformed_pbs_dir']
        parser = PbsScriptParser(self._config, self._event_defs)
        with open(file_name, 'r') as pbs_file:
            parser.parse_file(pbs_file)
        self.assertEquals(len(event_names), len(parser.events))
        for event in parser.events:
            self.assertTrue(event['id'] in event_names)
        self.assertEquals(len(event_names), parser.nr_errors)
