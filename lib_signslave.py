import chilkat2
import asyncio
import websockets
import time
import configparser
import json
import sys
import os
import ctypes


MessageBox = ctypes.windll.user32.MessageBoxW

# Async functions

def signdocument(crypt, inFile, sigFile):
    """
    Convert and file to .p7m format

    Arguments:
    inFile  - Path location of file to be signed
    sigFile - Path location of file signed
    """
    # Create the CAdES-BES signature, which contains the original data.
    success = crypt.CreateP7M(inFile, sigFile + ".p7m")
    if (success == False):
        payload = "File not found or file not reachable"
        error_box("error", payload)
        return False
    return True

# Sync functions

def load_file_logging(filepath):
    """
    Load the log file to write into it and return file

    Arguments:
    filepath - file location path.
    """
    # Open Log File
    if(os.path.exists(filepath)):
        f = open(filepath, "a+")
        return f
    else:
        return False


def readUSBCert(cert):
    """
    Load Certificate from USB Reader

    Arguments:
    cert - certificate object
    """
    return str(cert.SubjectCN)



def loadCert():
    # Use a certificate on a smartcard or USB token.

    certStore = chilkat2.CertStore()

    # Access the certificates on the smart card via the Chilkat certificate store class.
    success = certStore.OpenSmartcard("")
    if (success == False):
        print(certStore.LastErrorText)
        sys.exit()

    # Take the first verified certificate from the list
    cert = certStore.GetCertificate(0)

    print("Cert loaded from smartcard: " + cert.SubjectCN)

    # Provide the smartcard PIN.
    # If the PIN is not explicitly provided here, the Windows OS should
    # display a dialog for the PIN.
    cert.SmartCardPin = "55394274"
    return cert


def loadChilkat2():
    cert = loadCert()
    # Unlock the account
    glob = chilkat2.Global()
    success = glob.UnlockBundle("CAPERA.CB1072021_uvsZZSqn8v8g")

    # Note: Requires Chilkat v9.5.0.77 or greater.

    # This requires the Chilkat API to have been previously unlocked.
    # See Global Unlock Sample for sample code.

    crypt = chilkat2.Crypt2()

    # Provide the certificate for signing.
    success = crypt.SetSigningCert(cert)
    if (success != True):
        print(crypt.LastErrorText)
        sys.exit()

    # Indicate that SHA-256 should be used.
    crypt.HashAlgorithm = "sha256"

    # Specify the signed attributes to be included.
    # (This is what makes it CAdES-BES compliant.)
    jsonSignedAttrs = chilkat2.JsonObject()
    jsonSignedAttrs.UpdateInt("contentType", 1)
    jsonSignedAttrs.UpdateInt("signingTime", 1)
    jsonSignedAttrs.UpdateInt("messageDigest", 1)
    jsonSignedAttrs.UpdateInt("signingCertificateV2", 1)
    crypt.SigningAttributes = jsonSignedAttrs.Emit()
    return crypt


def format_to_log(type_msg, msg):
    """
    write on file errors and various type of log

    Arguments:
    type_msg - error, warning, simple log...
    msg      - the message to write
    """
    if type_msg == "error":
        payload = "[✘] " + msg + " [✘] - " + str(time.time())
        return str(payload.encode('utf8'))


def check_webdisk(filepath):
    """
    Check if webdisk is mounted in order to go
    straightforward.

    Arguments:
    filepath - check webdisk on path.
    """
    isFile = os.path.isdir(filepath)
    if isFile == False:
        print("Errore webdisk non e' montato")
        return False
    return True


def error_box(title, msg):
    """
    Error box, display an error message to the user,
    and log errors in file...

    Arguments:
    title - Window title.
    msg   - Content of the message box
    """
    MessageBox(None, 'Errore: ' + msg,
                   title, 0x10)
    return False


def message_box(title, msg):
    """
    Error box, display an error message to the user,
    and log errors in file...

    Arguments:
    title - Window title.
    msg   - Content of the message box
    """
    MessageBox(None, 'Errore: ' + msg,
                   title, 0x10)
    return False



def load_config(config_filepath):
    """
    A function that takes configuration file path, and returns
    his coniguration parsed. 

    Arguments:
    config_filepath - A string rappresenting the file path.
    """
    # Read .ini file
    config = configparser.ConfigParser()
    config.read(config_filepath)

    if(config.has_section("PATHs") == False):
        return error_box("Errore", "Impossibile caricare il percorso file specificato")
    
    return config
