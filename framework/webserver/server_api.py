"""
BSD 3-Clause License

Copyright (c) 2018, alessandrocomodi
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


"""
#
# The following file contains a set of functions that 
# allow the communication with the host application   
# through a UNIX socket.
#
# They are intended to be as general as possible. For the 
# sake of this example though we have specialized the python
# server in order to request specific images of the Mandelbrot
# set.
#
# Author: Alessandro Comodi, Politecnico di Milano
# 
"""

import struct
import base64
import socket

# Socket with host messages defines
CHUNK_SIZE    = 4096
MSG_LENGTH    = 128
ACK           = "\x00"

# Error Messages
INVALID_DATA  = "The client sent invalid data"

### This function serves to send general commands to the host application
### Parameters:
###   - sock    - socket channel with host
###   - message - command in byte array format
def socket_send_command(sock, message):
    # Send command message to host
    sock.send(message.encode())
    # Receive ACK
    response = sock.recv(MSG_LENGTH)

    return response.decode()

### This function requests an image to the FPGA
### Parameters:
###   - sock    - socket channel with host
###   - header  - command to be sent to the host
###   - payload - data for the image calculation
###   - b64  - to be eliminated
def get_image(sock, header, payload, b64=True):
  
  # Handshake with host application
  socket_send_command(sock, header)

  write_data_handler(sock, True, payload)

  # Synchronization with the host
  sock.send(ACK.encode())

  image = read_data_handler(sock, True, None, b64)
  return image

### This function writes data into the FPGA memory
### Parameters:
###   - sock        - socket channel with host
###   - isGetImage  - boolean value to understand if the request is 
###                 - performed within the GetImage context
###   - payload     - data to be written to memory
###   - header      - command to be sent to host (needed if isGetImage is False)
def write_data_handler(sock, isGetImage, payload, header=None):
  if not isGetImage:
    ###      Handshake      ###

    # Sending message type to host
    sock.send(header.encode())
    # Receive ACK
    sock.recv(MSG_LENGTH)
  
    ### Handshake terminated ###

  # Prepare payload
  # If message contains invalid data they will not be processed
  # Send JSON string size to the host.
  #print "Python sending JSON of length: %i" % len(payload)
  #print "JSON: ", payload
  sock.sendall(struct.pack("H", socket.htons(len(payload))))
  # Send JSON string to the host.
  sock.sendall(payload)

  # Receive ACK
  response = sock.recv(MSG_LENGTH)

  ### Communication with host terminated ###

  return response.decode()

### This function reads data from the FPGA memory
### Parameters:
###   - sock        - socket channel with host
###   - isGetImage  - boolean value to understand if the request is 
###                 - performed within the GetImage context
###   - header      - command to be sent to host (needed if isGetImage is False)
###   - b64         - encode a string in base64 and return base64(utf-8) string
###                   (else return binary string) (default=True)
def read_data_handler(sock, isGetImage, header=None, b64=True):
  if not isGetImage:
    ###      Handshake      ###

    # Sending message type to host
    sock.send(header.encode())
    # Receive response
    sock.recv(MSG_LENGTH)
    # Send ACK
    sock.send(ACK.encode())

    ### Handshake terminated ###
  
  # Receive integer data size from host
  response = sock.recv(4)
  # Decode data size 
  (size,) = struct.unpack("I", response)

  # Send ACK
  sock.send(ACK.encode())

  ### Receive chunks of data from host ###
  data = b''
  while len(data) < size:
    to_read = size - len(data)
    data += sock.recv(
        CHUNK_SIZE if to_read > CHUNK_SIZE else to_read)

  #byte_array = struct.unpack("<%uB" % size, data)
  if b64:
    data = base64.b64encode(data)

    # Does the decode("utf-8") below do anything? Let's check.
    tmp = data
    if (data != tmp.decode("utf-8")):
      print "FYI: UTF-8 check mismatched."

    data = data.decode("utf-8")

  return data
