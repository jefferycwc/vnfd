import requests
import json
from params import OPENSTACK_IP,OS_AUTH_URL,OS_USER_DOMAIN_NAME,OS_USERNAME,OS_PASSWORD,OS_PROJECT_DOMAIN_NAME,OS_PROJECT_NAME
from tacker_params import TACKER_IP,TACKER_OS_AUTH_URL,TACKER_OS_USER_DOMAIN_NAME,TACKER_OS_USERNAME,TACKER_OS_PASSWORD,TACKER_OS_PROJECT_DOMAIN_NAME,TACKER_OS_PROJECT_NAME

#response = requests.get("http://192.168.1.134/identity/v3/auth/tokens")

class TackerAPI():
    def __init__(self):
        self.TACKER_IP = TACKER_IP
	self.TACKER_OS_AUTH_URL = TACKER_OS_AUTH_URL
        self.TACKER_OS_USER_DOMAIN_NAME = TACKER_OS_USER_DOMAIN_NAME
        self.TACKER_OS_USERNAME = TACKER_OS_USERNAME
        self.TACKER_OS_PASSWORD = TACKER_OS_PASSWORD
        self.TACKER_OS_PROJECT_DOMAIN_NAME = TACKER_OS_PROJECT_DOMAIN_NAME
        self.TACKER_OS_PROJECT_NAME = TACKER_OS_PROJECT_NAME
        self.ary_data = []
        self.nsd_id = ''
        self.nsd_name = ''
        self.get_token_result = ''
        self.project_id = ''

    def get_token(self):
        # print("\nGet token:")
        self.get_token_result = ''
        get_token_url = self.TACKER_OS_AUTH_URL + 'auth/tokens'
        get_token_body = {
            'auth': {
                'identity': {
                    'methods': [
                        'password'
                    ],
                    'password': {
                        'user': {
                            'domain': {
                                'name': self.TACKER_OS_USER_DOMAIN_NAME
                            },
                            'name': self.TACKER_OS_USERNAME,
                            'password': self.TACKER_OS_PASSWORD
                        }
                    }
                },
                'scope': {
                    'project': {
                        'domain': {
                            'name': self.TACKER_OS_PROJECT_DOMAIN_NAME
                        },
                        'name': self.TACKER_OS_PROJECT_NAME
                    }
                }
            }
        }
        get_token_response = requests.post(get_token_url, data=json.dumps(get_token_body))
        #print("Get Tacker token status: " + str(get_token_response.status_code))
        self.get_token_result = get_token_response.headers['X-Subject-Token']
        return self.get_token_result

    def get_project_id(self, project_name):
        # print("\nGet Project ID:")
        self.project_id = ''
        get_project_list_url = self.TACKER_OS_AUTH_URL + 'projects'
        token = self.get_token()
        headers = {'X-Auth-Token': token}
        get_project_list_response = requests.get(get_project_list_url, headers=headers)
        print("Get Tacker project list status: " + str(get_project_list_response.status_code))
        get_project_list_result = get_project_list_response.json()['projects']
        #print(get_project_list_result)
        for project in get_project_list_result:
            if project['name'] == project_name:
                self.project_id = project['id']
            pass
        print("Project ID:" + self.project_id)
        return self.project_id

    def create_nsd(self, nsd_name, nsd_file_name):
        post_create_nsd_url = 'http://' + self.TACKER_IP + ':9890/v1.0/nsds'
        token = self.get_token()
	headers = {'X-Auth-Token': token}
	tenant_id = self.get_project_id(self.TACKER_OS_PROJECT_NAME)
	
	vnfd_name = self.parse_nsd_file(nsd_file_name)
	#print(vnfd_name)
	#print(len(vnfd_name))
	node_templates = self.generate_node_templates(len(vnfd_name))
	#node_templates = json.dumps(node_templates)
	nsd_description = 'NSD:' + nsd_name
	nsd_body = {
            'nsd': {
                'tenant_id': tenant_id,
                'name': nsd_name,
                'description': nsd_description,
                'attributes': {
                    'nsd': {
		      "imports": 
		        vnfd_name,
		      "tosca_definitions_version": "tosca_simple_profile_for_nfv_1_0_0",
                      "topology_template": {
                        "node_templates": node_templates
			#"node_templates": {
			#  "VNF1": {
			#    "type": "tosca.nodes.nfv.VNF1"
			#  },
			#  "VNF2": {
			#    "type": "tosca.nodes.nfv.VNF2"
			#  }
			#}
                      }
		    }
                },
            }
        }
	
	print(json.dumps(nsd_body))
	response = requests.post(post_create_nsd_url, data=json.dumps(nsd_body), headers=headers)
	print('Create NSD status: ' + str(response.status_code))
        #nsd_id = response.json()['nsd']['id']
	#print(nsd_id)

    def create_ns(self, ns_name, nsd_name, vim_name):
        post_create_ns_url = 'http://' + self.TACKER_IP + ':9890/v1.0/nss'
        token = self.get_token()
	headers = {'X-Auth-Token': token}
	tenant_id = self.get_project_id(self.TACKER_OS_PROJECT_NAME)
	nsd_id = self.get_nsd_id(nsd_name)
	ns_description = 'NS:' + ns_name
        vim_id = self.get_vim_id(vim_name)
	ns_body = {
            'ns': {
                'name': ns_name,
                'description': ns_description,
                'tenant_id': tenant_id,
                'nsd_id': nsd_id,
                'vim_id': vim_id,
            }
        }
	
	#print(nsd_body)
	response = requests.post(post_create_ns_url, data=json.dumps(ns_body), headers=headers)
	print('Create NS status: ' + str(response.status_code))
        result = response.json()
        print(result)

    def create_vnf(self, vnf_name, vnfd_name, vim_name):
        post_create_vnf_url = 'http://' + self.TACKER_IP + ':9890/v1.0/vnfs'
        token = self.get_token()
        headers = {'X-Auth-Token': token}
        tenant_id = self.get_project_id(self.TACKER_OS_PROJECT_NAME)
        vnfd_id = self.get_vnfd_id(vnfd_name)
        vnf_description = 'VNF:' + vnf_name
            vim_id = self.get_vim_id(vim_name)
        vnf_body = {
                'vnf': {
                    'name': vnf_name,
                    'description': vnf_description,
                    'tenant_id': tenant_id,
                    'vnfd_id': vnfd_id,
                    'vim_id': vim_id,
                }
        }
	
	#print(nsd_body)
	response = requests.post(post_create_vnf_url, data=json.dumps(vnf_body), headers=headers)
	print('Create VNF status: ' + str(response.status_code))
        result = response.json()
        print(result)

    def parse_nsd_file(self, nsd_file_name):
        vnfd_num = 0
        vnfd_name = []
        tag = 0

	## Open file
	fp = open(nsd_file_name, "r")
	line = fp.readline()
	while line:
	    #print(line)
	    check = line.split()
            if len(check) != 0 and check[0] == 'imports:':
              tag = 1
            if tag == 1:
	        line = fp.readline()
                x = line.split()
                #print(x)
	        if len(x) != 0 and x[0] == '-':
                  vnfd_name.append(x[1])
                  vnfd_num = vnfd_num + 1
                else:
                  tag = 0 
	    else:
	      line = fp.readline()
        fp.close()

        #print(vnfd_name)
	#print(len(vnfd_name))
	return vnfd_name

    def list_vim(self):
        get_vim_list_url = 'http://' + self.TACKER_IP + ':9890/v1.0/vims'
        token = self.get_token()
        headers = {'X-Auth-Token': token}
        get_vim_list_response = requests.get(get_vim_list_url, headers=headers)
        print("Get Tacker vim list status: " + str(get_vim_list_response.status_code))
        get_vim_list_result = get_vim_list_response.json()
        #text = get_vim_list_response.text
        #print(get_vim_list_result)
        #print(text)
        return get_vim_list_result     

    def get_vim_id(self, vim_name):
        vim_list = self.list_vim()
        #print(vim_list)
        vim_id = None
        for vim in vim_list['vims']:
            if vim['name'] == vim_name:
                vim_id = vim['id']
                print vim_id
            pass
        return vim_id

    def list_nsd(self):
        get_nsd_list_url = 'http://' + self.TACKER_IP + ':9890/v1.0/nsds'
        token = self.get_token()
        headers = {'X-Auth-Token': token}
        get_nsd_list_response = requests.get(get_nsd_list_url, headers=headers)
        print("Get Tacker nsd list status: " + str(get_nsd_list_response.status_code))
        get_nsd_list_result = get_nsd_list_response.json()
        #text = get_nsd_list_response.text
        #print(get_nsd_list_result)
        #print(text)
        return get_nsd_list_result     

    def get_nsd_id(self, nsd_name):
        nsd_list = self.list_nsd()
        #print(nsd_list)
        nsd_id = None
        for nsd in nsd_list['nsds']:
            if nsd['name'] == nsd_name:
                nsd_id = nsd['id']
                print nsd_id
            pass
        return nsd_id

    def list_vnfd(self):
        get_vnfd_list_url = 'http://' + self.TACKER_IP + ':9890/v1.0/vnfds'
        token = self.get_token()
        headers = {'X-Auth-Token': token}
        get_vnfd_list_response = requests.get(get_vnfd_list_url, headers=headers)
        print("Get Tacker vnfd list status: " + str(get_vnfd_list_response.status_code))
        get_vnfd_list_result = get_vnfd_list_response.json()
        #text = get_nsd_list_response.text
        #print(get_nsd_list_result)
        #print(text)
        return get_vnfd_list_result    

    def get_vnfd_id(self, vnfd_name):
        vnfd_list = self.list_vnfd()
        #print(vnfd_list)
        vnfd_id = None
        for vnfd in vnfd_list['vnfds']:
            if vnfd['name'] == vnfd_name:
                vnfd_id = vnfd['id']
                print vnfd_id
            pass
        return vnfd_id

    def generate_node_templates(self, number_of_vnf):
        node_templates = {}
        for i in range(number_of_vnf):
            vnf_s = "VNF" + str(i+1)
            vnf_t = "tosca.nodes.nfv.VNF" + str(i+1)
            vnf_d = {
                vnf_s: {
                    "type":vnf_t,
                }
            }
        node_templates.update(vnf_d)
        #print(vnf_d)
	
        print(node_templates)
        return node_templates

    def list_vnf(self):
        get_vnf_list_url = 'http://' + self.TACKER_IP + ':9890/v1.0/vnfs'
        token = self.get_token()
        headers = {'X-Auth-Token': token}
        get_vnf_list_response = requests.get(get_vnf_list_url, headers=headers)
        print("Get Tacker vnf list status: " + str(get_vnf_list_response.status_code))
        get_vnf_list_result = get_vnf_list_response.json()
        nrf_name = get_vnf_list_result['vnf']['name']
        printf(nrf_name)
        #text = get_vnf_list_response.text
        print(get_vnf_list_result)
        #print(text)
        return get_vnf_list_result

    def list_ns(self):
        get_ns_list_url = 'http://' + self.TACKER_IP + ':9890/v1.0/nss'
        token = self.get_token()
        headers = {'X-Auth-Token': token}
        get_ns_list_response = requests.get(get_ns_list_url, headers=headers)
        print("Get Tacker ns list status: " + str(get_ns_list_response.status_code))
        get_ns_list_result = get_ns_list_response.json()
        #text = get_vnf_list_response.text
        print(get_ns_list_result)
        #print(text)
        return get_ns_list_result

class OpenStackAPI():
    def __init__(self):
        #super().__init__()
        self.OPENSTACK_IP = OPENSTACK_IP
        self.OS_AUTH_URL = OS_AUTH_URL
        self.OS_USER_DOMAIN_NAME = OS_USER_DOMAIN_NAME
        self.OS_USERNAME = OS_USERNAME
        self.OS_PASSWORD = OS_PASSWORD
        self.OS_PROJECT_DOMAIN_NAME = OS_PROJECT_DOMAIN_NAME
        self.OS_PROJECT_NAME = OS_PROJECT_NAME
        self.ary_data = []
        self.nsd_id = ''
        self.nsd_name = ''
        self.get_token_result = ''
        self.project_id = ''

    def get_token(self):
        # print("\nGet token:")
        self.get_token_result = ''
        get_token_url = self.OS_AUTH_URL + '/v3/auth/tokens'
        get_token_body = {
            'auth': {
                'identity': {
                    'methods': [
                        'password'
                    ],
                    'password': {
                        'user': {
                            'domain': {
                                'name': self.OS_USER_DOMAIN_NAME
                            },
                            'name': self.OS_USERNAME,
                            'password': self.OS_PASSWORD
                        }
                    }
                },
                'scope': {
                    'project': {
                        'domain': {
                            'name': self.OS_PROJECT_DOMAIN_NAME
                        },
                        'name': self.OS_PROJECT_NAME
                    }
                }
            }
        }
        get_token_response = requests.post(get_token_url, data=json.dumps(get_token_body))
        #print("Get OpenStack token status: " + str(get_token_response.status_code))
        self.get_token_result = get_token_response.headers['X-Subject-Token']
        return self.get_token_result

    def get_project_id(self, project_name):
        # print("\nGet Project ID:")
        self.project_id = ''
        get_project_list_url = self.OS_AUTH_URL + '/v3/projects'
        token = self.get_token()
        headers = {'X-Auth-Token': token}
        get_project_list_response = requests.get(get_project_list_url, headers=headers)
        print("Get OpenStack project list status: " + str(get_project_list_response.status_code))
        get_project_list_result = get_project_list_response.json()['projects']
        #print(get_project_list_result)
        for project in get_project_list_result:
            if project['name'] == project_name:
                self.project_id = project['id']
            pass
        print("Project ID:" + self.project_id)
        return self.project_id

    def list_networks(self):
        get_network_list_url = 'http://' + self.OPENSTACK_IP + ':9696/v2.0/networks'
        token = self.get_token()
        headers = {'X-Auth-Token': token}
        get_network_list_response = requests.get(get_network_list_url, headers=headers)
        print("Get OpenStack network list status: " + str(get_network_list_response.status_code))
        get_network_list_result = get_network_list_response.json()
        #text = get_network_list_response.text
        #print(get_network_list_result)
        #print(text)
        return get_network_list_result

    def get_network_id(self, network_name):
        network_list = self.list_networks()
        #print(network_list)
        network_id = None
        for network in network_list['networks']:
            if network['name'] == network_name:
                network_id = network['id']
                print network_id
            pass
        return network_id

    def update_network(self, network_name, qos_policy_name):
        network_id = self.get_network_id(network_name)
        qos_policy_id = self.check_qos_policy_name(qos_policy_name)
        #print(qos_policy_id)
        update_network_url = 'http://' + self.OPENSTACK_IP + ':9696/v2.0/networks/' + network_id
        update_network_body = {
            "network": {
                "qos_policy_id": qos_policy_id
            }
        }
        token = self.get_token()
        headers = {'X-Auth-Token': token}
        response = requests.put(update_network_url, data=json.dumps(update_network_body), headers=headers)
        print('update network: ' + str(response.status_code))
        print(response.json())
        #if response.status_code == 201:
        #    get_rule_id = response.json()['bandwidth_limit_rule']
        #    rule_id = get_rule_id['id']
        #    print("Rule ID:" + rule_id)
        #    return rule_id
        #else:
        #    get_error = response.json()['NeutronError']
        #    print(get_error)


    def show_network_detail(self, network_name):
        network_id = self.get_network_id(network_name)
        show_network_detail_url = 'http://' + self.OPENSTACK_IP + ':9696/v2.0/networks/' + network_id
        token = self.get_token()
        headers = {'X-Auth-Token': token}
        show_network_detail_response = requests.get(show_network_detail_url, headers=headers)
        print("Show OpenStack network detail status: " + str(show_network_detail_response.status_code))
        show_network_detail_result = show_network_detail_response.json()
        #text = get_network_list_response.text
        print(show_network_detail_result)
        #print(text)

    def list_qos_policy(self):
        get_qos_policy_url = 'http://' + self.OPENSTACK_IP + ':9696/v2.0/qos/policies/'
        token = self.get_token()
        headers = {'X-Auth-Token': token}
        get_qos_policy_list_response = requests.get(get_qos_policy_url, headers=headers)
        print("Get OpenStack qos policy status: " + str(get_qos_policy_list_response.status_code))
        get_qos_policy_list_result = get_qos_policy_list_response.json()
        #print(get_qos_policy_list_result)
        return get_qos_policy_list_result
   
    def check_qos_policy_name(self, qos_policy_name):
        qos_policy_list = self.list_qos_policy()
        #print(qos_policy_list)
        policy_id = None
        for policy in qos_policy_list['policies']:
            if policy['name'] == qos_policy_name:
                print("QoS policy: name already exists")
                #print(policy)
                policy_id = policy['id']
                print(policy_id)
            pass
        return policy_id


    def create_qos_policy(self, qos_policy_name, description_content):
        policy_id = self.check_qos_policy_name(qos_policy_name)
        if policy_id == None:
            post_qos_policy_url = 'http://' + self.OPENSTACK_IP + ':9696/v2.0/qos/policies/'
            policy_body = {
                "policy": {
                    "name": qos_policy_name,
                    "description": description_content,
                    "shared": "False"
                }
            }
            token = self.get_token()
            headers = {'X-Auth-Token': token}
            response = requests.post(post_qos_policy_url, data=json.dumps(policy_body), headers=headers)
            print('create qos policy: ' + str(response.status_code))
            get_qos_policy_id = response.json()['policy']
            #print(response.json())
            #print(get_qos_policy_id)
            policy_id = get_qos_policy_id['id']
        print("Policy ID:" + policy_id)
        return policy_id
    
    def create_bandwidth_limit_rule(self, qos_policy_id, max_kbps, max_burst_kbps, direction):
        post_bandwidth_limit_rule_url = 'http://' + self.OPENSTACK_IP + ':9696/v2.0/qos/policies/' + qos_policy_id + '/bandwidth_limit_rules'
        bandwidth_limit_body = {
            "bandwidth_limit_rule": {
                "max_kbps": max_kbps,
                "max_burst_kbps": max_burst_kbps,
                "direction": direction
            }
        }
        token = self.get_token()
        headers = {'X-Auth-Token': token}
        response = requests.post(post_bandwidth_limit_rule_url, data=json.dumps(bandwidth_limit_body), headers=headers)
        print('create bandwidth limit rule: ' + str(response.status_code))
        #print(response.json())
        if response.status_code == 201:
            get_rule_id = response.json()['bandwidth_limit_rule']
            rule_id = get_rule_id['id']
            print("Rule ID:" + rule_id)
            return rule_id
        else:
            get_error = response.json()['NeutronError']
            print(get_error)

    def update_bandwidth_limit_rule(self, qos_policy_id, rule_id, max_kbps, max_burst_kbps, direction):
        put_bandwidth_limit_rule_url = 'http://' + self.OPENSTACK_IP + ':9696/v2.0/qos/policies/' + qos_policy_id + '/bandwidth_limit_rules/' + rule_id
        #print(put_bandwidth_limit_rule_url)
        bandwidth_limit_body = {
            "bandwidth_limit_rule": {
                "max_kbps": max_kbps,
                "max_burst_kbps": max_burst_kbps,
                "direction": direction
            }
        }
        token = self.get_token()
        headers = {'X-Auth-Token': token}
        response = requests.put(put_bandwidth_limit_rule_url, data=json.dumps(bandwidth_limit_body), headers=headers)
        print('update bandwidth limit rule: ' + str(response.status_code))
        print(response.json())

    def list_port(self):
        get_port_url = 'http://' + self.OPENSTACK_IP + ':9696/v2.0/ports'
        token = self.get_token()
        headers = {'X-Auth-Token': token}
        get_port_list_response = requests.get(get_port_url, headers=headers)
        print("Get OpenStack port status: " + str(get_port_list_response.status_code))
        get_port_list_result = get_port_list_response.json()
        #print(get_port_list_result)
        return get_port_list_result

    def get_port_id(self, port_ip):
        port_list = self.list_port()
        #print(network_list)
        port_id = None
        for port in port_list['ports']:
	    #print port
	    for fixed_ip in port['fixed_ips']:
		#print fixed_ip['ip_address']
                if fixed_ip['ip_address'] == port_ip:
                    port_id = port['id']
                    print port_id
                pass
	    pass
        return port_id

def parse_bandwidth(file_name):
    output = {}
    network_name = dict()
    egress = dict()
    ingress = dict()
    fp = open(file_name, "r")
    line = fp.readline()
    while line:
        #print(line)
        line = fp.readline()
	check = line.split()
        if len(check) != 0 and check[0] == 'bandwidth:':
            print("start parsing bandwidth")
            while line:
                line = fp.readline()
                each_value = line.split()
                if len(each_value) == 0:
                    break
                else:
                    if each_value[0] == 'network_name:':
                        network_name['network_name'] = each_value[1]
                    elif each_value[0] == 'direction:':
                        temp = dict()
                        if each_value[1] == 'egress':
                            for i in range(2):
                                line = fp.readline()
                                kbps_value = line.split()
                                temp_kbps = dict()
                                temp_kbps[kbps_value[0]] = kbps_value[1]
                                temp.update(temp_kbps)
                            egress['egress'] = temp
                        elif each_value[1] == 'ingress':
                            for i in range(2):
                                line = fp.readline()
                                kbps_value = line.split()
                                temp_kbps = dict()
                                temp_kbps[kbps_value[0]] = kbps_value[1]
                                temp.update(temp_kbps)
                            ingress['ingress'] = temp
    output.update(network_name)
    output.update(egress)
    output.update(ingress)
    #print(output)
    fp.close()
    return output
###
#  network_name: test
#  direction: egress
#  max_kbps: 10000
#  max_burst_kbps: 10000
###

def initiate_ns(file_name, nsd_name, vim_name):
    output = parse_bandwidth(file_name)
    print(output)
    #print(len(output))
    #print(output["network_name"])
    #print(output["egress"]["max_kbps:"])
    #print(output["ingress"])
    #if "egress" in output:
    #    print(output["egress"])
    #if "ingress" in output:
    #    print(output["ingress"])

    if vim_name == "OpenStack_Site":
        ### onboard NSD, create NS
        test = TackerAPI()
        test.create_nsd(nsd_name,file_name)
        test.create_ns(nsd_name,nsd_name,vim_name)

        if len(output)!=0:
            test = OpenStackAPI()
            qos_policy_id = test.create_qos_policy(output["network_name"],output["network_name"])
            if len(output)==3:
                test.create_bandwidth_limit_rule(qos_policy_id, output["egress"]["max_kbps:"], output["egress"]["max_burst_kbps:"], "egress")
                test.create_bandwidth_limit_rule(qos_policy_id, output["ingress"]["max_kbps:"], output["ingress"]["max_burst_kbps:"], "ingress")
            else:
                if "egress" in output:
                    test.create_bandwidth_limit_rule(qos_policy_id, output["egress"]["max_kbps:"], output["egress"]["max_burst_kbps:"], "egress")
                if "ingress" in output:
                    test.create_bandwidth_limit_rule(qos_policy_id, output["ingress"]["max_kbps:"], output["ingress"]["max_burst_kbps:"], "ingress")
            test.update_network(output["network_name"],output["network_name"])
            test.show_network_detail(output["network_name"])

    elif vim_name == "Kubernetes_Site":
        print("Kubernetes")
        test = TackerAPI()
        vnfd_name = test.parse_nsd_file(file_name)
        print(vnfd_name)
        for i in range(len(vnfd_name)):
            #vnfd_id = test.get_vnfd_id(vnfd_name[i])
            vnf_name = nsd_name + "_" + str(i+1)
            #print(vnf_name)
            test.create_vnf(vnf_name, vnfd_name[i], vim_name)
    

if __name__ == '__main__':
    print('start')
    test = TackerAPI()
    test.list_vnf()
    #get_vnf_status()
    #initiate_ns("k8s_nsd.yaml","om2m_k8s_NS","Kubernetes_Site")
    #initiate_ns("iottalk_nsd.yaml","IoTtalk_NS","OpenStack_Site")
    
    #test = OpenStackAPI()
    #test.get_project_id(OS_PROJECT_NAME)
    #test.list_networks()
    #qos_policy_id = test.create_qos_policy("123","test")
    #test.list_qos_policy()
    #test.check_qos_policy_name("123")
    #qos_policy_id = test.create_qos_policy("test","test")
    #rule_id = test.create_bandwidth_limit_rule(qos_policy_id, 10000, 0, "egress")
    #test.create_bandwidth_limit_rule(qos_policy_id, 10000, 0, "ingress")
    #test.update_bandwidth_limit_rule(qos_policy_id, rule_id, 10000, 0, "egress")
    #test.update_bandwidth_limit_rule(qos_policy_id, "a82543bf-65d8-435d-8a8b-a32c1ff2f5fa", 1000000, 0, "egress")
    #test.get_network_id("test")
    #test.show_network_detail("test")
    #test.update_network("test_qos","test")
    #test.show_network_detail("test")
    
    #test = TackerAPI()
    #test.get_project_id(TACKER_OS_PROJECT_NAME)
    #test.parse_nsd_file("nsd.yaml")
    #test.parse_nsd_file("free5GC-NSD.yaml")
    #test.create_nsd("NSD_TEST1", "nsd.yaml")
    #test.create_nsd("NSD_TEST", "1.yaml")
    #test.create_ns("TEST_NS","NSD_TEST","OpenStack_Site")
    #test.get_vim_id("OpenStack_Site")
    #test.generate_node_templates(9)

    #parse_bandwidth("1.yaml")
    #initiate_ns("3.yaml","OM2M_NS","OpenStack_Site")
    #initiate_ns("iottalk_nsd.yaml","IoTtalk_NS","OpenStack_Site")

    #test = TackerAPI()
    #test.create_vnf("om2m_cnf_test", "OM2M_CNFD_TEST", "Kubernetes_Site")

    #test = TackerAPI()
    #test.list_ns()

    #test = OpenStackAPI()
    #test.list_port()
    #test.get_port_id("192.168.3.177")



