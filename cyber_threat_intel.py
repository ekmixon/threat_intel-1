'''
Author: @midnightslacker
Date: 02/22/2020
Description: Open source threat intelligence feeds aggregator. 
             Output to file and create a csv for SIEM ingestion.     
'''

#!/usr/bin/env python3
import requests
import re
import os
import sys
import shutil

'''
# SOURCES NO LONGER AVAILABLE
    DRG_vncProbe = "https://www.dragonresearchgroup.org/insight/vncprobe.txt"
    DRG_http = "https://www.dragonresearchgroup.org/insight/http-report.txt"
    DRG_ssh = "https://www.dragonresearchgroup.org/insight/sshpwauth.txt"
    virbl_dns_blacklist = "http://virbl.org/download/virbl.dnsbl.bit.nl.txt"
    talos_blacklist = "http://www.talosintel.com/feeds/ip-filter.blf"
    packet_mail_ip = "https://www.packetmail.net/iprep.txt"
    packet_mail_ET = "https://www.packetmail.net/iprep_emerging_ips.txt"
    blockList = "http://www.blocklist.de/lists/all.txt"
    angler = "http://www.beerandraptors.com/dontcrawlmebro/angler_ips"
'''

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3',
}

#IPs
file_path = os.environ['HOME']+"/dev/output/threat_sources/"
output_file = os.environ['HOME']+"/dev/output/threats.csv"
output_dir = os.environ['HOME']+"/dev/output/"

#Domains
domain_path = os.environ['HOME']+"/dev/output/threat_domains/"
domain_output = os.environ['HOME']+"/dev/output/threat_domains.csv"

#AlienVault
alien = "https://reputation.alienvault.com/reputation.generic"

#Abuse.ch
zeus = "https://zeustracker.abuse.ch/blocklist.php?download=ipblocklist"
palevo = "https://palevotracker.abuse.ch/blocklists.php?download=ipblocklist"
feodo = "https://feodotracker.abuse.ch/blocklist/?download=ipblocklist"

#Emerging Threats
ethreat_blockedIP =        "http://rules.emergingthreats.net/fwrules/emerging-Block-IPs.txt"
ethreat_compromisedIP =    "http://rules.emergingthreats.net/blockrules/compromised-ips.txt"
ethreat_RBN_malvertisers = "http://doc.emergingthreats.net/pub/Main/RussianBusinessNetwork/emerging-rbn-malvertisers.txt"

#Malc0de Black List
malcode = "http://malc0de.com/bl/IP_Blacklist.txt"

#OpenBL.org
openBL = "http://www.openbl.org/lists/base.txt"

#NoThink.org -- DNS, HTTP and IRC
ntTelnet = "http://www.nothink.org/honeypots/honeypot_telnet_blacklist_2019.txt"
ntSSH = "http://www.nothink.org/honeypots/honeypot_ssh_blacklist_2019.txt"

#Project Honey Pot
honey_pot = "http://www.projecthoneypot.org/list_of_ips.php?rss=1"

#CI Army
ci_army = "http://www.ciarmy.com/list/ci-badguys.txt"

#danger.rules.sk
danger_rules = "http://danger.rulez.sk/projects/bruteforceblocker/blist.php"

#SANS
sans_ip = "https://isc.sans.edu/ipsascii.html"

#autoshun.org
autoshun = "http://www.autoshun.org/files/shunlist.csv"

#charles.the-haleys.org -- SSH dictionary attack
ssh_dict_attack = "http://charles.the-haleys.org/ssh_dico_attack_hdeny_format.php/hostsdeny.txt"

#TOR  nodes
tor_exit_nodes = "https://check.torproject.org/exit-addresses"

#osint.bambenekconuslting.com
osint_iplist = "http://osint.bambenekconsulting.com/feeds/c2-ipmasterlist.txt"


open_source_threat_intel = {
    "AlienVault_blacklist":alien,
    "malc0de_blacklist":malcode, 
    "palevo_ip_blacklist":palevo,  
    "zeus_tracker_ip_blacklist":zeus,
    "feodo_black_list":feodo,
    "emerging_threats_compromised_ips":ethreat_compromisedIP,
    "emerging_threats_malvertisers":ethreat_RBN_malvertisers,
    "noThink_SSH_blacklist":ntSSH,
    "noThink_Telnet_blacklist":ntTelnet,
    "ci_army":ci_army,
    "danger_rules":danger_rules,
    "isc_SANS":sans_ip,
    "autoshun":autoshun,
    "ssh_bruteforce":ssh_dict_attack,
    "tor_exit_nodes":tor_exit_nodes,
    "osint_iplist":osint_iplist
    }

# Regular expression for IPv4 Addresses
ip = re.compile('((?:(?:[12]\d?\d?|[1-9]\d|[1-9])\.){3}(?:[12]\d?\d?|[\d+]{1,2}))')

def regex(threat_list, pattern):
    ''' Filter pattern from threat_list '''
    threat_intel = re.findall(pattern, str(threat_list))
    return '\n'.join(threat_intel)

def urlgrab (host, pattern):
    ''' Grab threat intel from host '''
    try:
        response = requests.get(host, headers=HEADERS, timeout=5)
        response.raise_for_status()
        threat_list = response.content
        return regex(threat_list, pattern)
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

def writeToFile(source_path, threat_list, filename):
    ''' Write updated threat intel to correct file and directory '''
    # check if file already exists, if it does, overwrite it. If the file doesn't exist, create it.
    if os.path.isfile(source_path+filename):
        f = open(source_path+filename, 'r+')
        f.writelines(threat_list)
        f.truncate()
    else:
        f = open(source_path+filename, 'w+')
        f.writelines(threat_list)

    f.close()

def createCSV(source_path, directory, oFile, header):
    ''' Create a two column csv file with threat and source for the columns '''
    # Make sure the directory is mounted
    if not os.path.isdir(directory):
        print "\t [-] Output directory does not exist or is not mounted\n"
        sys.exit()

    # copy old file for diff--then remove to create new file
    if os.path.isfile(oFile):
        shutil.copyfile(oFile, oFile+".old")
        os.remove(oFile)
    
    # create header for first line
    f = open(oFile, 'w+')
    f.write(header)
    
    for hFile in os.listdir(source_path):
        with open(source_path+hFile) as infile:
            for line in infile:
                f.write(line.rstrip()+","+hFile+"\n")
    f.close()

def main():
    # Loop through open source threat intelligence sources
    # Pull them down from the interwebs and format them
    # Write them to file.
    for filename, source in open_source_threat_intel.iteritems():
        print(f"[+] Grabbing: {source}")
        threat_list=urlgrab(source, ip)
        writeToFile(file_path, threat_list, filename)

    # Create CSV
    print("[+] Creating CSV. . .\n")
    createCSV(file_path, output_dir, output_file, "IP,Threat_Feed\n")

    # Now lets create a domain blacklist -- sources are handled by bash script
    createCSV(domain_path, output_dir, domain_output, "Domain, Threat_Feed\n")

if __name__ == "__main__":
    main()

