# -*- coding: utf-8 -*-
# 
# Script : network_scanner/core/controller/packet/l4_udp_data.py
# Author : Hoon
# 
# ====================== Comments ======================
# 

UDP_DATA = {
    'by_port': {}
}

UDP_DATA[ 'by_port' ][ 7 ] = \
b"\x0d\x0a\x0d\x0a"
# Echo
#     Echo data: 0d0a0d0a

UDP_DATA[ 'by_port' ][ 53 ] = \
b"\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00"
# Domain Name System (query)
#     Transaction ID: 0x0000
#     Flags: 0x1000 Server status request
#         0... .... .... .... = Response: Message is a query
#         .001 0... .... .... = Opcode: Server status request (2)
#         .... ..0. .... .... = Truncated: Message is not truncated
#         .... ...0 .... .... = Recursion desired: Don't do query recursively
#         .... .... .0.. .... = Z: reserved (0)
#         .... .... ...0 .... = Non-authenticated data: Unacceptable
#     Questions: 0
#     Answer RRs: 0
#     Authority RRs: 0
#     Additional RRs: 0
#     [Response In: 427]

UDP_DATA[ 'by_port' ][ 111 ] = \
b"\x72\xfe\x1d\x13\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01\x86\xa0" \
b"\x00\x01\x97\x7c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
b"\x00\x00\x00\x00\x00\x00\x00\x00"
# Remote Procedure Call, Type:Call XID:0x72fe1d13
#     XID: 0x72fe1d13 (1929256211)
#     Message Type: Call (0)
#     RPC Version: 2
#     Program: Portmap (100000)
#     Program Version: 104316
#     Procedure: proc-0 (0)
#     Duplicate Call/Reply
#     Duplicate to the call in: 596
#     Credentials
#         Flavor: AUTH_NULL (0)
#         Length: 0
#     Verifier
#         Flavor: AUTH_NULL (0)
#         Length: 0

UDP_DATA[ 'by_port' ][ 123 ] = \
b"\xe3\x00\x04\xfa\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00" \
b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
b"\x00\x00\x00\x00\x00\x00\x00\x00\xc5\x4f\x23\x4b\x71\xb1\x52\xf3"
# Network Time Protocol (NTP Version 4, client)
#     Flags: 0xe3, Leap Indicator: unknown (clock unsynchronized), Version number: NTP Version 4, Mode: client
#         11.. .... = Leap Indicator: unknown (clock unsynchronized) (3)
#         ..10 0... = Version number: NTP Version 4 (4)
#         .... .011 = Mode: client (3)
#     Peer Clock Stratum: unspecified or invalid (0)
#     Peer Polling Interval: 4 (16 seconds)
#     Peer Clock Precision: 0.015625 seconds
#     Root Delay: 1.000000 seconds
#     Root Dispersion: 1.000000 seconds
#     Reference ID: NULL
#     Reference Timestamp: Feb  7, 2036 06:28:16.000000000 UTC
#     Origin Timestamp: Feb  7, 2036 06:28:16.000000000 UTC
#     Receive Timestamp: Feb  7, 2036 06:28:16.000000000 UTC
#     Transmit Timestamp: Nov 24, 2004 15:12:11.444111999 UTC

UDP_DATA[ 'by_port' ][ 137 ] = \
b"\x80\xf0\x00\x10\x00\x01\x00\x00\x00\x00\x00\x00\x20\x43\x4b\x41" \
b"\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41" \
b"\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x00\x00\x21" \
b"\x00\x01"
# NetBIOS Name Service
#     Transaction ID: 0x80f0
#     Flags: 0x0010, Opcode: Name query, Broadcast
#         0... .... .... .... = Response: Message is a query
#         .000 0... .... .... = Opcode: Name query (0)
#         .... ..0. .... .... = Truncated: Message is not truncated
#         .... ...0 .... .... = Recursion desired: Don't do query recursively
#         .... .... ...1 .... = Broadcast: Broadcast packet
#     Questions: 1
#     Answer RRs: 0
#     Authority RRs: 0
#     Additional RRs: 0
#     Queries
#         *<00><00><00><00><00><00><00><00><00><00><00><00><00><00><00>: type NBSTAT, class IN
#             Name: *<00><00><00><00><00><00><00><00><00><00><00><00><00><00><00> (Workstation/Redirector)
#             Type: NBSTAT (33)
#             Class: IN (1)
'''
UDP_DATA[ 'by_port' ][ 137 ] = \
b"\x13\x37\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x20\x43\x4b\x41" \
b"\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41" \
b"\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x00\x00\x21" \
b"\x00\x01"
# NetBIOS Name Service
#     Transaction ID: 0x1337
#     Flags: 0x0000, Opcode: Name query, Broadcast
#         0... .... .... .... = Response: Message is a query
#         .000 0... .... .... = Opcode: Name query (0)
#         .... ..0. .... .... = Truncated: Message is not truncated
#         .... ...0 .... .... = Recursion desired: Don't do query recursively
#         .... .... ...0 .... = Broadcast: Broadcast packet
#     Questions: 1
#     Answer RRs: 0
#     Authority RRs: 0
#     Additional RRs: 0
#     Queries
#         *<00><00><00><00><00><00><00><00><00><00><00><00><00><00><00>: type NBSTAT, class IN
#             Name: *<00><00><00><00><00><00><00><00><00><00><00><00><00><00><00> (Workstation/Redirector)
#             Type: NBSTAT (33)
#             Class: IN (1)
'''

UDP_DATA[ 'by_port' ][ 161 ] = \
b"\x30\x3a\x02\x01\x03\x30\x0f\x02\x02\x4a\x69\x02\x03\x00\xff\xe3" \
b"\x04\x01\x04\x02\x01\x03\x04\x10\x30\x0e\x04\x00\x02\x01\x00\x02" \
b"\x01\x00\x04\x00\x04\x00\x04\x00\x30\x12\x04\x00\x04\x00\xa0\x0c" \
b"\x02\x02\x37\xf0\x02\x01\x00\x02\x01\x00\x30\x00"
# Simple Network Management Protocol
#     msgVersion: snmpv3 (3)
#     msgGlobalData
#         msgID: 19049
#         msgMaxSize: 65507
#         msgFlags: 04
#             .... .1.. = Reportable: Set
#             .... ..0. = Encrypted: Not set
#             .... ...0 = Authenticated: Not set
#         msgSecurityModel: USM (3)
#     msgAuthoritativeEngineID: <MISSING>
#     msgAuthoritativeEngineBoots: 0
#     msgAuthoritativeEngineTime: 0
#     msgUserName: 
#     msgAuthenticationParameters: <MISSING>
#     msgPrivacyParameters: <MISSING>
#     msgData: plaintext (0)
#         plaintext
#             contextEngineID: <MISSING>
#             contextName: 
#             data: get-request (0)
#                 get-request
#                     request-id: 14320
#                     error-status: noError (0)
#                     error-index: 0
#                     variable-bindings: 0 items

UDP_DATA[ 'by_port' ][ 177 ] = \
b"\x00\x01\x00\x02\x00\x01\x00"
# X Display Manager Control Protocol
#     Version: 1
#     Opcode: Query (0x0002)
#     Message length: 1
#     Authentication names (0)

UDP_DATA[ 'by_port' ][ 389 ] = \
b"\x30\x84\x00\x00\x00\x2d\x02\x01\x07\x63\x84\x00\x00\x00\x24\x04" \
b"\x00\x0a\x01\x00\x0a\x01\x00\x02\x01\x00\x02\x01\x64\x01\x01\x00" \
b"\x87\x0b\x6f\x62\x6a\x65\x63\x74\x43\x6c\x61\x73\x73\x30\x84\x00" \
b"\x00\x00\x00"
# Connectionless Lightweight Directory Access Protocol
#     LDAPMessage searchRequest(7) "<ROOT>" baseObject
#         messageID: 7
#         protocolOp: searchRequest (3)
#             searchRequest
#                 baseObject: 
#                 scope: baseObject (0)
#                 derefAliases: neverDerefAliases (0)
#                 sizeLimit: 0
#                 timeLimit: 100
#                 typesOnly: False
#                 Filter: (objectClass=*)
#                     filter: present (7)
#                         present: objectClass
#                 attributes: 0 items

UDP_DATA[ 'by_port' ][ 427 ] = \
b"\x02\x01\x00\x00\x36\x20\x00\x00\x00\x00\x00\x01\x00\x02\x65\x6e" \
b"\x00\x00\x00\x15\x73\x65\x72\x76\x69\x63\x65\x3a\x73\x65\x72\x76" \
b"\x69\x63\x65\x2d\x61\x67\x65\x6e\x74\x00\x07\x64\x65\x66\x61\x75" \
b"\x6c\x74\x00\x00\x00\x00"
# Service Location Protocol
#     Version: 2
#     Function: Service Request (1)
#     Packet Length: 54
#     Flags: 0x2000, Multicast requested
#         0... .... .... .... = Overflow: Message will fit in a datagram
#         .0.. .... .... .... = Fresh Registration: Not a new Service Registration
#         ..1. .... .... .... = Multicast requested: Multicast (or broadcast) request
#     Next Extension Offset: 0
#     XID: 1
#     Lang Tag Len: 2
#     Lang Tag: en
#     Previous Response List Length: 0
#     Service Type Length: 21
#     Service Type List: service:service-agent
#     Scope List Length: 7
#     Scope List: default
#     Predicate Length: 0
#     SLP SPI Length: 0

UDP_DATA[ 'by_port' ][ 443 ] = \
b"\x16\xfe\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x36\x01\x00\x00" \
b"\x2a\x00\x00\x00\x00\x00\x00\x00\x2a\xfe\xfd\x00\x00\x00\x00\x7c" \
b"\x77\x40\x1e\x8a\xc8\x22\xa0\xa0\x18\xff\x93\x08\xca\xac\x0a\x64" \
b"\x2f\xc9\x22\x64\xbc\x08\xa8\x16\x89\x19\x3f\x00\x00\x00\x02\x00" \
b"\x2f\x01\x00"
# Datagram Transport Layer Security
#     DTLS Record Layer: Handshake Protocol: Client Hello
#         Content Type: Handshake (22)
#         Version: DTLS 1.0 (0xfeff)
#         Epoch: 0
#         Sequence Number: 0
#         Length: 54
#         Handshake Protocol: Client Hello
#             Handshake Type: Client Hello (1)
#             Length: 42
#             Message Sequence: 0
#             Fragment Offset: 0
#             Fragment Length: 42
#             Version: DTLS 1.2 (0xfefd)
#             Random: 000000007c77401e8ac822a0a018ff9308caac0a642fc922…
#                 GMT Unix Time: Jan  1, 1970 09:00:00.000000000 대한민국 표준시
#                 Random Bytes: 7c77401e8ac822a0a018ff9308caac0a642fc92264bc08a8…
#             Session ID Length: 0
#             Cookie Length: 0
#             Cipher Suites Length: 2
#             Cipher Suites (1 suite)
#                 Cipher Suite: TLS_RSA_WITH_AES_128_CBC_SHA (0x002f)
#             Compression Methods Length: 1
#             Compression Methods (1 method)
#                 Compression Method: null (0)

UDP_DATA[ 'by_port' ][ 500 ] = \
b"\x00\x11\x22\x33\x44\x55\x66\x77\x00\x00\x00\x00\x00\x00\x00\x00" \
b"\x01\x10\x02\x00\x00\x00\x00\x00\x00\x00\x00\xc0\x00\x00\x00\xa4" \
b"\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x98\x01\x01\x00\x04" \
b"\x03\x00\x00\x24\x01\x01\x00\x00\x80\x01\x00\x05\x80\x02\x00\x02" \
b"\x80\x03\x00\x01\x80\x04\x00\x02\x80\x0b\x00\x01\x00\x0c\x00\x04" \
b"\x00\x00\x00\x01\x03\x00\x00\x24\x02\x01\x00\x00\x80\x01\x00\x05" \
b"\x80\x02\x00\x01\x80\x03\x00\x01\x80\x04\x00\x02\x80\x0b\x00\x01" \
b"\x00\x0c\x00\x04\x00\x00\x00\x01\x03\x00\x00\x24\x03\x01\x00\x00" \
b"\x80\x01\x00\x01\x80\x02\x00\x02\x80\x03\x00\x01\x80\x04\x00\x02" \
b"\x80\x0b\x00\x01\x00\x0c\x00\x04\x00\x00\x00\x01\x00\x00\x00\x24" \
b"\x04\x01\x00\x00\x80\x01\x00\x01\x80\x02\x00\x01\x80\x03\x00\x01" \
b"\x80\x04\x00\x02\x80\x0b\x00\x01\x00\x0c\x00\x04\x00\x00\x00\x01"
# Internet Security Association and Key Management Protocol
#     Initiator SPI: 0011223344556677
#     Responder SPI: 0000000000000000
#     Next payload: Security Association (1)
#     Version: 1.0
#         0001 .... = MjVer: 0x1
#         .... 0000 = MnVer: 0x0
#     Exchange type: Identity Protection (Main Mode) (2)
#     Flags: 0x00
#         .... ...0 = Encryption: Not encrypted
#         .... ..0. = Commit: No commit
#         .... .0.. = Authentication: No authentication
#     Message ID: 0x00000000
#     Length: 192
#     Payload: Security Association (1)
#         Next payload: NONE / No Next Payload  (0)
#         Reserved: 00
#         Payload length: 164
#         Domain of interpretation: IPSEC (1)
#         Situation: 00000001
#             .... .... .... .... .... .... .... ...1 = Identity Only: True
#             .... .... .... .... .... .... .... ..0. = Secrecy: False
#             .... .... .... .... .... .... .... .0.. = Integrity: False
#         Payload: Proposal (2) # 1
#             Next payload: NONE / No Next Payload  (0)
#             Reserved: 00
#             Payload length: 152
#             Proposal number: 1
#             Protocol ID: ISAKMP (1)
#             SPI Size: 0
#             Proposal transforms: 4
#             Payload: Transform (3) # 1
#                 Next payload: Transform (3)
#                 Reserved: 00
#                 Payload length: 36
#                 Transform number: 1
#                 Transform ID: KEY_IKE (1)
#                 Reserved: 0000
#                 IKE Attribute (t=1,l=2): Encryption-Algorithm: 3DES-CBC
#                     1... .... .... .... = Format: Type/Value (TV)
#                     Type: Encryption-Algorithm (1)
#                     Value: 0005
#                     Encryption Algorithm: 3DES-CBC (5)
#                 IKE Attribute (t=2,l=2): Hash-Algorithm: SHA
#                     1... .... .... .... = Format: Type/Value (TV)
#                     Type: Hash-Algorithm (2)
#                     Value: 0002
#                     HASH Algorithm: SHA (2)
#                 IKE Attribute (t=3,l=2): Authentication-Method: Pre-shared key
#                     1... .... .... .... = Format: Type/Value (TV)
#                     Type: Authentication-Method (3)
#                     Value: 0001
#                     Authentication Method: Pre-shared key (1)
#                 IKE Attribute (t=4,l=2): Group-Description: Alternate 1024-bit MODP group
#                     1... .... .... .... = Format: Type/Value (TV)
#                     Type: Group-Description (4)
#                     Value: 0002
#                     Group Description: Alternate 1024-bit MODP group (2)
#                 IKE Attribute (t=11,l=2): Life-Type: Seconds
#                     1... .... .... .... = Format: Type/Value (TV)
#                     Type: Life-Type (11)
#                     Value: 0001
#                     Life Type: Seconds (1)
#                 IKE Attribute (t=12,l=4): Life-Duration: 1
#                     0... .... .... .... = Format: Type/Length/Value (TLV)
#                     Type: Life-Duration (12)
#                     Length: 4
#                     Value: 00000001
#                     Life Duration: 1
#             Payload: Transform (3) # 2
#                 Next payload: Transform (3)
#                 Reserved: 00
#                 Payload length: 36
#                 Transform number: 2
#                 Transform ID: KEY_IKE (1)
#                 Reserved: 0000
#                 IKE Attribute (t=1,l=2): Encryption-Algorithm: 3DES-CBC
#                     1... .... .... .... = Format: Type/Value (TV)
#                     Type: Encryption-Algorithm (1)
#                     Value: 0005
#                     Encryption Algorithm: 3DES-CBC (5)
#                 IKE Attribute (t=2,l=2): Hash-Algorithm: MD5
#                     1... .... .... .... = Format: Type/Value (TV)
#                     Type: Hash-Algorithm (2)
#                     Value: 0001
#                     HASH Algorithm: MD5 (1)
#                 IKE Attribute (t=3,l=2): Authentication-Method: Pre-shared key
#                     1... .... .... .... = Format: Type/Value (TV)
#                     Type: Authentication-Method (3)
#                     Value: 0001
#                     Authentication Method: Pre-shared key (1)
#                 IKE Attribute (t=4,l=2): Group-Description: Alternate 1024-bit MODP group
#                     1... .... .... .... = Format: Type/Value (TV)
#                     Type: Group-Description (4)
#                     Value: 0002
#                     Group Description: Alternate 1024-bit MODP group (2)
#                 IKE Attribute (t=11,l=2): Life-Type: Seconds
#                     1... .... .... .... = Format: Type/Value (TV)
#                     Type: Life-Type (11)
#                     Value: 0001
#                     Life Type: Seconds (1)
#                 IKE Attribute (t=12,l=4): Life-Duration: 1
#                     0... .... .... .... = Format: Type/Length/Value (TLV)
#                     Type: Life-Duration (12)
#                     Length: 4
#                     Value: 00000001
#                     Life Duration: 1
#             Payload: Transform (3) # 3
#                 Next payload: Transform (3)
#                 Reserved: 00
#                 Payload length: 36
#                 Transform number: 3
#                 Transform ID: KEY_IKE (1)
#                 Reserved: 0000
#                 IKE Attribute (t=1,l=2): Encryption-Algorithm: DES-CBC
#                     1... .... .... .... = Format: Type/Value (TV)
#                     Type: Encryption-Algorithm (1)
#                     Value: 0001
#                     Encryption Algorithm: DES-CBC (1)
#                 IKE Attribute (t=2,l=2): Hash-Algorithm: SHA
#                     1... .... .... .... = Format: Type/Value (TV)
#                     Type: Hash-Algorithm (2)
#                     Value: 0002
#                     HASH Algorithm: SHA (2)
#                 IKE Attribute (t=3,l=2): Authentication-Method: Pre-shared key
#                     1... .... .... .... = Format: Type/Value (TV)
#                     Type: Authentication-Method (3)
#                     Value: 0001
#                     Authentication Method: Pre-shared key (1)
#                 IKE Attribute (t=4,l=2): Group-Description: Alternate 1024-bit MODP group
#                     1... .... .... .... = Format: Type/Value (TV)
#                     Type: Group-Description (4)
#                     Value: 0002
#                     Group Description: Alternate 1024-bit MODP group (2)
#                 IKE Attribute (t=11,l=2): Life-Type: Seconds
#                     1... .... .... .... = Format: Type/Value (TV)
#                     Type: Life-Type (11)
#                     Value: 0001
#                     Life Type: Seconds (1)
#                 IKE Attribute (t=12,l=4): Life-Duration: 1
#                     0... .... .... .... = Format: Type/Length/Value (TLV)
#                     Type: Life-Duration (12)
#                     Length: 4
#                     Value: 00000001
#                     Life Duration: 1
#             Payload: Transform (3) # 4
#                 Next payload: NONE / No Next Payload  (0)
#                 Reserved: 00
#                 Payload length: 36
#                 Transform number: 4
#                 Transform ID: KEY_IKE (1)
#                 Reserved: 0000
#                 IKE Attribute (t=1,l=2): Encryption-Algorithm: DES-CBC
#                     1... .... .... .... = Format: Type/Value (TV)
#                     Type: Encryption-Algorithm (1)
#                     Value: 0001
#                     Encryption Algorithm: DES-CBC (1)
#                 IKE Attribute (t=2,l=2): Hash-Algorithm: MD5
#                     1... .... .... .... = Format: Type/Value (TV)
#                     Type: Hash-Algorithm (2)
#                     Value: 0001
#                     HASH Algorithm: MD5 (1)
#                 IKE Attribute (t=3,l=2): Authentication-Method: Pre-shared key
#                     1... .... .... .... = Format: Type/Value (TV)
#                     Type: Authentication-Method (3)
#                     Value: 0001
#                     Authentication Method: Pre-shared key (1)
#                 IKE Attribute (t=4,l=2): Group-Description: Alternate 1024-bit MODP group
#                     1... .... .... .... = Format: Type/Value (TV)
#                     Type: Group-Description (4)
#                     Value: 0002
#                     Group Description: Alternate 1024-bit MODP group (2)
#                 IKE Attribute (t=11,l=2): Life-Type: Seconds
#                     1... .... .... .... = Format: Type/Value (TV)
#                     Type: Life-Type (11)
#                     Value: 0001
#                     Life Type: Seconds (1)
#                 IKE Attribute (t=12,l=4): Life-Duration: 1
#                     0... .... .... .... = Format: Type/Length/Value (TLV)
#                     Type: Life-Duration (12)
#                     Length: 4
#                     Value: 00000001
#                     Life Duration: 1

UDP_DATA[ 'by_port' ][ 520 ] = \
b"\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
b"\x00\x00\x00\x00\x00\x00\x00\x10"
# Routing Information Protocol
#     Command: Request (1)
#     Version: RIPv1 (1)
#     Address not specified, Metric: 16
#         Address Family: Unspecified (0)
#         Metric: 16

UDP_DATA[ 'by_port' ][ 623 ] = \
b"\x06\x00\xff\x07\x00\x00" \
b"\x00\x00\x00\x00\x00\x00\x00\x09\x20\x18\xc8\x81\x00\x38\x8e\x04\xb5"
# Remote Management Control Protocol, Class: IPMI
#     Version: 0x06
#     Reserved: 0x00
#     Sequence: 0xff
#     Type: Normal RMCP, Class: IPMI
#         ...0 0111 = Class: IPMI (0x07)
#         0... .... = Message Type: Normal RMCP (0x0)
# IPMI v1.5 Session Wrapper, session ID 0x0
#     Authentication Type: NONE (0x00)
#     Session Sequence Number: 0x00000000
#     Session ID: 0x00000000
#     Message Length: 9
# Intelligent Platform Management Bus
#     Bus command data: 2018c88100388e04b5
# Data (9 bytes)
#     Data: 2018c88100388e04b5
#     [Length: 9]

UDP_DATA[ 'by_port' ][ 1645 ] = \
b"\x01\x00\x00\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
b"\x00\x00\x00\x00"
# RADIUS Protocol
#     Code: Access-Request (1)
#     Packet identifier: 0x0 (0)
#     Length: 20
#     Authenticator: 00000000000000000000000000000000

UDP_DATA[ 'by_port' ][ 2049 ] = \
b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01\x86\xa3" \
b"\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
b"\x00\x00\x00\x00\x00\x00\x00\x00"
# Remote Procedure Call, Type:Call XID:0x00000000
#     XID: 0x00000000 (0)
#     Message Type: Call (0)
#     RPC Version: 2
#     Program: NFS (100003)
#     Program Version: 2
#     Procedure: NULL (0)
#     Credentials
#         Flavor: AUTH_NULL (0)
#         Length: 0
#     Verifier
#         Flavor: AUTH_NULL (0)
#         Length: 0
# Network File System
#     [Program Version: 2]
#     [V2 Procedure: NULL (0)]

UDP_DATA[ 'by_port' ][ 5351 ] = \
b"\x00\x00"
# NAT Port Mapping Protocol, External Address Request
#     Version: 0
#     Opcode: External Address Request (0)

UDP_DATA[ 'by_port' ][ 5353 ] = \
b"\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x09\x5f\x73\x65" \
b"\x72\x76\x69\x63\x65\x73\x07\x5f\x64\x6e\x73\x2d\x73\x64\x04\x5f" \
b"\x75\x64\x70\x05\x6c\x6f\x63\x61\x6c\x00\x00\x0c\x00\x01"
# Multicast Domain Name System (query)
#     Transaction ID: 0x0000
#     Flags: 0x0000 Standard query
#         0... .... .... .... = Response: Message is a query
#         .000 0... .... .... = Opcode: Standard query (0)
#         .... ..0. .... .... = Truncated: Message is not truncated
#         .... ...0 .... .... = Recursion desired: Don't do query recursively
#         .... .... .0.. .... = Z: reserved (0)
#         .... .... ...0 .... = Non-authenticated data: Unacceptable
#     Questions: 1
#     Answer RRs: 0
#     Authority RRs: 0
#     Additional RRs: 0
#     Queries
#         _services._dns-sd._udp.local: type PTR, class IN, "QM" question
#             Name: _services._dns-sd._udp.local
#             [Name Length: 28]
#             [Label Count: 4]
#             Type: PTR (domain name PoinTeR) (12)
#             .000 0000 0000 0001 = Class: IN (0x0001)
#             0... .... .... .... = "QU" question: False