# FPGA-Webserver Overview

This project provides a communication layer between web applications and Cloud FPGA accelerators in order to enhance the performance of compute-intensive tasks. Further documentation for this project, including the project vision, can be found in this [Google Drive Folder](https://drive.google.com/drive/folders/1EdhyuvQmIN18YxHsRkTGffVvuAwmHfkJ?usp=sharing). This project utilizes Amazon AWS F1 instances and the corresponding Xilinx tools (Vivado, SDAccel).

This repository contains the generic framework as well as sample applications that utilize the framework.

# Status

While the layer is intended to be generic, in its current form, this repo contains both generic functionality and components that are specific to the initial demonstration application -- a [Mandelbrot explorer](https://github.com/alessandrocomodi/fpga-webserver/tree/master/apps/mandelbrot).


# Project description

A hardware accelerated web application utilizing this framework consists of:

  - Web Client: a web application, or any other agent communicating with the accelerated server via web protocols.
  - Web Server: a web server written in Python
  - Host Application: the host application written in C/C++/OpenCL which interfaces with the hardware.

The WebSocket or REST communication between the Web Application and the FPGA passes through:

  1. The Web Client application, written in JavaScript running in a web browser, transmits JSON (for now), via WebSocket or GET, to the Web Server. The communication is currently simple commands containing:
      - type: describes the command that has to be performed by the host application and dispatched to the FPGA;
      - data: a data value to be sent to the FPGA.
  1. The Web Server, a Python web server, echoes commands via UNIX socket to the Host Application.
  1. The Host Application, written in C/C++/OpenCL, transmits the commands to the FPGA Shell through OpenCL calls.
  1. The FPGA Shell, written in Verilog and configured by scripts, communicates between memory and the Custom Kernel via AXI and FIFOs.
  1. The Custom Kernel, provided as Verilog, and for Mandelbrot written in TL-Verilog, processes the data stream from the FPGA Shell and produces a data stream returned to the FPGA Shell
  1. The FPGA Shell transmits the data stream to the Host Application. For Mandelbrot, this data is depth values for each pixel.
  1. The Host Application, for Mandelbrot, processes pixel depths into colors, and into a `.png` data stream, which is returned over the UNIX socket to the Web Server.
  1. The Web Server echoes the data stream to the client via the WebSocket or as a GET response.
  1. The Web Cient displays the image.


# Directory Structure

  - `framework`: The generic infrastructure for hardware-accelerated web applications.
    - `client`: Client library.
    - `webserver`: Python web server application.
    - `host`: OpenCL/C++ host application framework.
    - `fpga`: FPGA framework, including Verilog/TLV source code.
    - `f1`: Specific to Amazon F1.
  - `apps`: Hardware-accelerated web applications utilizing the framework.
    - _app_
      - `client`
      - `webserver`
      - `host`
      - `fpga`: FPGA kernel, including Verilog/TLV source code.
        - `scripts`: Utility scripts needed to create a Vivado RTL project that holds all the configurations (e.g. # AXI master ports, # scalar arguments, # arguments) for the hardware.
      - `build`
        - `Makefile`
      - `out`: The target directory for build results, including the client, webserver, host application, and FPGA images. (This folder is not committed with the repository.)
      - `prebuilt`: Prebuilt client, webserver, host application, and/or FPGA images. These may be committed for convenience so users can run new installations without lengthy builds.
    - _(specific apps)_
    - `echo`: (To be created.) A template application that simply echoes data on a websocket
      - `client`
      - `host`
      - `fpga`
      - `build`
        - `Makefile`
    - `mandelbrot`
      - `client`
      - `webserver`
      - `host`
      - `fpga`
      - `build`
        - `Makefile`


# Project Setup Overview

Setup for AWS F1 and building from scratch is a very lengthy process. Optional instructions are provided to get the Mandelbrot application up and running on a local Linux machine without FPGA acceleration. Furthermore, to run with FPGA acceleration, prebuilt images are provided to initially bypass the lengthy builds.

As a preview of the complete process, to get up and running from source code with FPGA acceleration, you will need to:

  - Get an AWS account with access to F1 instances. This is a lengthy process requiring a few days to get approval from Amazon.
  - Launch a "Build Instance" on which to compile the OpenCL, Verilog, and Transaction-Level Verilog source code into an FPGA image.
  - Launch an "F1 Server Instance" on which to run: the web server, the Host Application, and the FPGA programmed with the image you created on the Build Instance.
  - Open the Web Application in a local web browser (or host it on a web server) and connect to the running Web Server.

(Keep in mind, there is a far more substantial world of hurt that this infrastructure is saving you.)

Note that F1 machines are powerful and expensive. Compilations take several hours and require a sizable Build Instance which can cost a few dollars per compilation. F1 machines cost about $1.50/hr, so it is not practical to keep a server up and running for extended periods.


# AWS Account Setup with F1 Access

Finally, I found some good instructions from Xilinx. The instructions I came up with are below, but you should be able instead to follow the "Prerequisites" instructions <a href="https://github.com/Xilinx/SDAccel-Tutorials/blob/master/docs/aws-getting-started/RTL/README.md" target="_ blank">here</a>.

## Previous instructions

(These can be deleted once the Xilinx instructions are confirmed to serve the same purpose.)

If you are new to AWS, you might find it to be quite complicated. Here are some specific steps to get you going, though they likely need refinement. Be sure to correct these docs based on your experience.

  1. Create a <a href="https://aws.amazon.com/free/" target="_ blank">free tier account</a> and await approval.
  1. Login to your console. Be sure you are logging in as root, not as an IAM user. (Your account has no "IAM" users until you create them (which is not necessary to get going).)
  1. Now, you'll need access to F1 resources (and possibly the Amazon Machine Image (AMI) for the Build Instance). Unless policies change, you must apply for this. You can try skipping ahead to confirm.
    - Under "Support" (upper left) open "Support Center".
    - Create a case.
      - Regarding: "Service Limit Increase".
      - Limit Type: "EC2 Instances"
      - Region: "N. Virginia" (and possibly other options)
      - Primary Instance Type: "f1.2xlarge"
      - Use Case Description: Something like, "Development of hardware-accelerated web applications using this framework (https://github.com/alessandrocomodi/fpga-webserver)"
      - Wait ~2 business days :(


# Running Mandelbrot Locally

While you wait for F1 access, you can play around with the Mandelbrot example without hardware acceleration.

On a Ubuntu 16.04 machine:
```sh
sudo apt-get update
sudo apt-get install make g++ python python-pip python-pil
cd <wherever you would like to work>
git clone https://github.com/alessandrocomodi/fpga-webserver
cd fpga-webserver
git submodule update --init --recursive  # or ./init
cd apps/mandelbrot/build
make launch
```

The webserver is running. You can open `http://localhost:8888/index.html` in a local web browser and explore Mandelbrot generated in the Python webserver or in the C++ host application.

You can also open `http://localhost:8888/client.html`. Click "Open", click "Init FPGA", enter coords, like 0, 0, zoom: 1, depth 100, "GET IMAGE" or "Start" for a flythrough.

More instructions for the Mandelbrot application are [here](https://github.com/alessandrocomodi/fpga-webserver/tree/master/apps/mandelbrot).


# F1 Instance Setup

Now let's provision an F1 Instance. Again, I came up instructions below, but you should be able to use the "Create, configure, and test an AWS F1 instance" instructions from Xilinx, <a href="https://github.com/Xilinx/SDAccel-Tutorials/blob/master/docs/aws-getting-started/RTL/README.md" target="_ blank">here</a>.

You will want to open one or more additional ports for the Web Server. From the "Running Instances" page (via EC2 Dashboard), scroll right and select the security group for your instance. Under "Inbound":

  - "Add Rule"
  - For "Type" select "Custom TCP Rule" (should be the default), and enter "8880-8889" as port range (by default, we will use port 8888, but let's reserve several).
  - Select or enter a "Source", e.g. "Anywhere" or your IP address for better security.
  - Set "Description", e.g. "development-webserver".

Note that you should already have a port open for RDP. (I am using VNC, so I also opened custom TCP ports 5901-5910.)

Log into your instance:
```sh
ssh -i <AWS key pairs.pem> centos@<ip>`
```

Now, configure your `~/.bashrc`. We will share files between instances using Amazon S3 through folders called `s3://fpga-webserver/<unique-username>`, so choose a username for yourself, such as your Amazon IAM username, and:

```sh
echo 'export S3_USER=<unique-username>' >> ~/.bashrc
source ~/.bashrc
```

Use the same user name for all your instances.

## Previous instructions

(These can be deleted once the Xilinx process is confirmed to cover all of this.)

  1. From the dashboard, click "Launch Instance".
  1. Note the tabs at the top for the steps to select, configure, and launch our instance.
  1. You are currently in "Choose AMI".
    1. Click "AWS Marketplace" on the left.
    1. Enter "FPGA" in the search box.
    1. Select "FPGA Developer AMI".
    1. "Continue".
  1. You are now in "Choose Instance Type". (See tabs and heading at the top).
    1. Select f1.2xlarge (in "North Virginia").
  1. Default configuration is generally good, but we do need to open up a few ports. We'll open 8888 as the default development port for the webserver. And, we'll open a port for remote desktops. Jump ahead by clicking the tab "Configure Security Group".
    1. Provide a name for a new security group (e.g. "fpga-webserver-dev") and a description (e.g. "For development using https://github.com/alessandrocomodi/fpga-webserver").
    1. For webserver:
      1. "Add Rule"
      1. For "Type" select "Custom TCP Rule" (should be the default), and enter "8880-8889" as port range (by default, we will use port 8888, but let's reserve several).
      1. Select or enter a "Source", e.g. "Anywhere" or your IP address for better security.
      1. Set "Description", e.g. "development-webserver".
    1. For RDP (Remote Desktop Protocol):
      1. "Add Rule"
      1. For "Type" select "RDP"
      1. Enter "Source" and "Description" appropriately.
    1. For VNC (Virtual Network Computing):
      1. "Add Rule"
      1. For "Type" select "Custom TCP Rule", and enter "5901-5910" as port range.
      1. Enter "Source" and "Description" appropriately.
  1. Click "Review and Launch", be sure you are comfortable with any warnings, review details, and "Launch".
  1. Create/select a key pair for access to your new instance. (You'll need to read up on SSH keys and `ssh-keygen` if you are not familiar. These instructions assume a public key file `<AWS key pairs.pem>`. (Be sure to `chmod 400 ~<AWS key pairs.pem>`.)) "Launch".
  1. Click new instance link to find IP address.
  1. You can view your instances from the left panel. Go to your EC2 Dashboard and click "Running Instances" or under "Instances", select "Instances". From here, you can, among other things, start and stop your instances ("Actions", "Instance State"). Be sure not to accidentally leave them running!!! You should configure monitoring of your resources, but the options seem very limited for catching instances you fail to stop. Also be warned that stopping an instance can fail. Be sure your instance transitions to "stopped" state (or Amazon tells me charging stops at "stopping" state).

Log into your instance:
```sh
ssh -i <AWS key pairs.pem> centos@<ip>`
```

Now, configure your `~/.bashrc`. We will share files between instances using Amazon S3 through folders called `s3://fpga-webserver/<unique-username>`, so choose a username for yourself, such as your Amazon IAM username, and:

```sh
echo 'export S3_USER=<unique-username>' >> ~/.bashrc
source ~/.bashrc
```

Use the same user name for all your instances.


# Remote Work Environment

## X11 Forwarding

It is important to be able to run X11 applications on your instance and display them on your machine. You will probably get a `DISPLAY not set` message when first trying X forwarding with `ssh -X` and running an X application. I was able to fix this with:

```sh
sudo yum install xorg-x11-xauth  # On EC2 instance. Then log out and back in.
exit
ssh -X -i <AWS key pairs.pem> centos@<ip>
```

## Remote Desktop

(Delete this section once the Xilinx RDP setup instructions are validated. Maybe keep TigerVNC & Xfce instructions for linux users as it might run faster?)

It is also important to be able to run a remote desktop. Remote desktop protocols are generally faster than X11. This is less important for the F1 Instance than it is for the Build Instance, where you will be debugging your design, so you might choose to skip these instructions until you provision the Build Instance.

I first tried following an [AWS tutorial from Reinvent 2017](https://github.com/awslabs/aws-fpga-app-notes/tree/master/reInvent17_Developer_Workshop) that used RDP, but I was unsuccessful. (Note, that participants were provided a custom AMI to start from.)

### VNC from Linux Client

After much struggling, I was able to get VNC working with the Xfce desktop environment. Here are some notes, though I may have picked
up some necessary dependencies from my earlier attempts that are missing here.

```sh
sudo yum install tigervnc-server
vncpasswd  # Provide password for VNC desktop (and, optionally, a different password for view-only access)
```

```sh
sudo yum install -y epel-release
sudo yum groupinstall -y "Xfce"
```
(I do not think a reboot is necessary.)

Edit ~/.vnc/xstartup to contain:

```sh
#!/bin/sh
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
/etc/X11/xinit/xinitrc
[ -x /etc/vnc/xstartup ] && exec /etc/vnc/xstartup
[ -r $HOME/.Xresources ] && xrdb $HOME/.Xresources
vncconfig -iconic &
#xterm -geometry 80x24+10+10 -ls -title "$VNCDESKTOP Desktop" &
startxfce4 &
```

The VNC Server can be started with:

```sh
vncserver  # Optionally -geometry XXXXxYYYY.
```

The output of this command indicates a log file. You should take a look. I got a number of warnings, but they did not appear to be fatal.

And kill with:
```sh
vncserver -kill :1
```

Any number of clients can be connected to this server while it is running. Closing the client connection does not terminate the server.

From my Ubuntu client, I connected using Remmina. In Remmina, select `VNC`, enter `<EC2-IP>:1`, and "Connect!". Or define a connection using "New" and fill in "Name", "Protocol": "VNC", "Server": "<IP>", "User name", "Password", and click "Connect".


### RDP Desktop

In case it helps to debug issues, or in case you need to connect from Windows, this is what I did following the Reinvent 2017 instructions (without success):

In place of:
```sh
source <(curl -s https://s3.amazonaws.com/aws-ec2-f1-reinvent-17/setup_script/setup_reinvent.sh)
```

I extracted the following commands:
```sh
sudo yum install -y kernel-devel # Needed to re-build ENA driver
sudo yum groupinstall -y "Server with GUI"
sudo systemctl set-default graphical.target

sudo yum -y install epel-release
sudo rpm -Uvh http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-5.el7.nux.noarch.rpm
sudo yum install -y xrdp tigervnc-server
sudo yum install -y chromium
sudo systemctl start xrdp
sudo systemctl enable xrdp
sudo systemctl disable firewalld  # Probably non-existent
sudo systemctl stop firewalld     #  "
```

And I attepted to connect using Remmina from my Ubuntu machine without success.

# Running on FPGA

Prebuilt files are included in the repository. (TODO: No they are not.). Try to run using those first, so you can see the FPGA in action.

```sh
cd
git clone https://github.com/alessandrocomodi/fpga-webserver
cd fpga-webserver
git submodule update --init --recursive  # or ./init
cd apps/mandelbrot/build
make PREBUILT=true TARGET=hw KERNEL=mandelbrot launch
```

Point a web browser at `http://<IP>:8888` and play with the application.

When you are done, _`ctrl-C`_, `exit`, and stop your instance.


# Build Instance Setup

You can build on your F1 instance, but building takes a long time, and its cheaper to build on a machine that does not have the FPGA.

Provision a Build Instance as you did the F1 Instance, but use instance type "c4.4xlarge" (as recommended by Amazon, or we have found "c4.2xlarge" to suffice, though it's slower). `ssh` into this instance. It wouldn't hurt to open port 8888 on this instance as well in case you want to test on this instance without the FPGA.


# One-Time Instance Setup

## AWS CLI Configuration

Configure by providing your credentials. These can be found in in the Security Credentials page, which I'm not sure how to navigate to, but here's a <a href="https://console.aws.amazon.com/iam/home?#/security_credential" target="_ blank">direct link</a>.

Use region: `us-east-1` and output: `json`.

```sh
aws configure
```

## Clone Necessary Repos

```sh
cd
git clone https://github.com/aws/aws-fpga.git $AWS_FPGA_REPO_DIR
git clone https://github.com/alessandrocomodi/fpga-webserver
cd fpga-webserver
git submodule update --init --recursive  # or ./init
```


# With Each Login

```sh
source fpga-webserver/sdaccel_setup
```

# Building from Source

Now, build both the FPGA image and host application, transfer them to the F1 instance, and run as follows.

## FPGA Build

On your Build Instance, build host and Amazon FPGA Image (AFI) that the host application will load onto the FPGA.

```sh
cd ~/fpga-webserver/apps/mandelbrot/build
mkdir ../out
make build TARGET=hw KERNEL=mandelbrot -j8 > ../out/out.log &
```

TODO: What about hw_emu target and running in emulation?

This produces output files in `/fpga-webserver/apps/mandelbrot/out/hw/xilinx_aws-vu9p-f1_4ddr-xpr-2pr_4.0/`. Additionally, the final step, the AFI creation, produces a `.tar` file on S3 storage asynchronously in `s3://fpga-webserver/<user-id>/mandelbrot/AFIs/*.tar`. (You configured `<user-id>` in your `~/.bashrc`). You can see it with:

```sh
aws s3 ls s3://fpga-webserver/<user-id>/mandelbrot/AFIs/
```

It also produces `/fpga-webserver/apps/mandelbrot/out/hw/xilinx_aws-vu9p-f1_4ddr-xpr-2pr_4.0/mandelbrot.awsclbin` which references the S3 tarball.

# Transfer files and Run

All development is done on the Build Instance. The F1 Instance is just used to run. `fpga-webserver/apps/mandelbrot/` is transferred from the Build Instance to the F1 Instance in its entirety through S3 storage.

## Push

You can transfer your app directory to run on the FPGA using the `push` Make target (which runs an `aws s3 sync` command) and by explicitly running an `aws s3 sync` command to pull. Though the whole directory is copied, the files of importance are:

  - the python webserver (including client content) (everything in `fpga-webserver/apps/mandelbrot/webserver`)
  - the host application (built via intermediate Make target `host`)
  - the `.awsxclbin` (AFI) image (which references `s3://fpga-webserver/<user-id>/mandelbrot/AFIs/`)
  - `launch` script in `fpga-webserver/apps/mandelbrot/build`

```sh
cd ~/fpga-webserver/apps/mandelbrot/build
make push TARGET=hw KERNEL=mandelbrot &
```

## Pull

Now, start and log into your F1 Instance, initialize and configure AWS and pull these files:

```sh
mkdir ~/work
cd ~/work
mkdir mandelbrot
cd mandelbrot
aws s3 sync s3://fpga-webserver/<user-id>/mandelbrot/xfer .
```


## Launch

```sh
cd ~/mandelbrot_work/build
chmod +x launch ../out/*/*/host # execute privs lost in transfer
./launch hw
```

## Run

As you did locally, you can access `http://<IP>:8888/index.html`. Now you can utilize the FPGA to generate images.


# Development Using this Framework

## Makerchip and TL-Verilog

The Mandelbrot set accelerator has been developed in the [Makerchip](https://makerchip.com/) IDE using the TL-Verilog language extension.
You can copy into Makerchip, or use this link to
[open the design in makerchip](http://www.makerchip.com/sandbox?code_url=https:%2F%2Fraw.githubusercontent.com%2Falessandrocomodi%2Ffpga-webserver%2Fmaster%2Fapps%2Fmandelbrot%2Ffpga%2Fmandelbrot.tlv).
After the kernel has been designed in Makerchip we retrieved the Verilog files by clicking on "E" -> "Open Results" in the Editor tab. From the new browser tab the files that host the Verilog code are called "top.sv" and "top_gen.sv".
The content of these files has to be copied and pasted inside of the file "mandelbrot_example_adder.sv" found in the "fpga/imports" folder.


# Development of this Framework

These are WIP notes:

## SDAccel

This is how I was able to generate an RTL kernel in SDAccel manually and run hardware emulation. This is scripted as part of the build process, but not with the ability to run in SDAccel. These are notes to help figure that out.

 - `cd ~/fpga-webserver`
 - `source sdaccel_setup`
 - `sdx`
 - `echo $AWS_FPGA_REPO_DIR` (You will need to know this path.)
 - On Welcome screen "Add Custon Platform".
   - Add "$AWS_FPGA_REPO_DIR/SDAccel/aws_platform/xilinx_aws-vu9p-f1_?ddr-xpr-2pr_4_0".
 - "New SDxProject": name it, select only platform, accept linux on x86 and OpenCL runtime, and "Empty Application". "Finish".
 - Menu "Xilinx", "Create RTL Kernel".
   - name it; 2 clocks (independent kernel clock)
   - default scalars (or change them)
   - default AXI master (Global Memory) options (or change them)
   - wait for Vivado
 - In Vivado:
   - "Generate RTL Kernel"
   - wait
   - Close
 - Back in SDAccel:
   - in projects.sdx:
     - Add binary container under "Hardware Functions" by selecting the yellow add box thing. You will get "binary_container_1".
     - Select "Emulation-HW"
  - Menu "Run", "Run Configuration"
    - Tab "Main", "Kernel Debug", Check "Use RTL waveform...", and check "Launch live waveform".
    - Tab "Arguments", check "Automatically add binary container(s) to arguments"
    - Click "Run" (or "Apply" and click green circle w/ play arrow).


# Related Technologies

  - [Fletcher](https://github.com/johanpel/fletcher) might make a good foundation for this framework.

# To Do

  - Figure out how to generate .xo.
    - `framework/fpga/scripts/create_rtl_kernel.sh` creates parts of `mandelbrot/fpga/mandelbrot_hw` (`imports`?) which should be built through Makefile, not included in repo. (Paths have changed, so scripts are broken).
    - `mandelbrot/fpga/mandelbrot_hw/imports/package_kernel.tcl` produces `.xo` from `mandelbrot_hw`. (Not sure if it runs xocc itself or if that should be done in Makefile.)
  - hw_emu instructions.
  - Include initialization steps in host application automatically. (For `client.html`, no explicit commands to `open` and `Init FPGA`.)
  - provide information and pointers about the more general use of the commands.
  - Automate export from Makerchip by providing a script that uses `curl` to access result files via `http://makerchip.com/compile/<compile-id>/results/<filename>`.
  - Split mandelbrot Makefile to provide some parts in framework.


# Immediate Issues

  - apps/mandelbrot/out/ does not exist for make command above.
  - no pre-built files in apps/mandelbrot/prebuilt
  - still need to initialize FPGA w/ client.html?
  - failing w/ "ERROR: Failed to load xclbin" (sdx_imports/main.c). Solved by stopping & starting F1 Instance (not by rebooting).
