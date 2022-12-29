# ALL OF THE IMPORTS
#Cryptography import for key management and encryption
#Base64-encode the bytes-like object and return the encoded bytes
#socket is for the connection between the server and client
#tkinter for the GUI
#Continuous threading allows to manage concurrent threads

from cryptography.hazmat.backends import default_backend  
from cryptography.hazmat.primitives.asymmetric import rsa  
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.fernet import Fernet
import base64
import socket
from tkinter import *
import continuous_threading



class SecureChat: #The class containing all functions for the application

    def __init__(self, iHST, iPRT, imode, chatwindow):
        self.HST = iHST
        self.PRT = iPRT
        self.sock = None
        self.conn = None
        self.client_key = None
        self.private_key = None
        self.public_key = None
        self.private_pem = None
        self.public_pem = None
        self.mode = imode
        self.cwindow = chatwindow
        self.status = True
        self.rect = None
        
        self.gen_asym_keys() #Generate asymmetric keys for the server
        if self.mode == "server":
            self.gen_sym_key("server")
            self.status = self.server_connection()
            self.server_exchange() #exchange keys
        else:
            self.status = self.client_connection()
            self.client_exchange() 
            
        if self.status:            
            self.printmessage("Session started") 
            self.rect = continuous_threading.ContinuousThread(target=self.recv)
            self.rect.start()
        
    def __del__(self):
        self.printmessage("Session ended")
        if self.rect is not None:
            self.rect.stop()

    def server_connection(self): #Function to start the server
        self.printmessage(f"Starting server on {self.HST}:{self.PRT}") 
        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.HST, int(self.PRT))) #server binds itself to port number and host
            self.sock.listen(2)
            
            self.conn, addr = self.sock.accept() #create a server socket and listen for incoming connections.
            self.printmessage("Connected with client")
        except:
            self.printmessage("Error connecting to socket")
            return False
            
        return True
            

    def client_connection(self): #establishing connection to server from client
        self.printmessage(f"Connecting to server at {self.HST}:{self.PRT}")
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.conn.connect((self.HST, int(self.PRT))) #connect using the port and host number added by the user
            self.printmessage(f"Connected to server at {self.HST}:{self.PRT}")
        except:
            self.printmessage("Error connecting to server")
            return False
        return True

    def gen_sym_key(self, data): #generate the symmetric key
        global sym_key, FR  #starts by declaring a global variable called sym_key.
                    #Then, the code checks if data (the key) is equal to the server.
        if data == "server":
            sym_key = Fernet.generate_key() #generate key
        else:
            sym_key = data 
        FR = Fernet(sym_key) 

    def sym_encrypt(self, data): #encrypt the data
        b64_data = base64.b64encode(data.encode('utf-8')) 
        return(FR.encrypt(b64_data)) #uses base64 to encode the string, then encrypts it with FR.encrypt() 

        #The code above first converts the string of text into a binary string using base64 encoding,
        # then calls the function FR.encrypt() which returns the encrypted string in binary form.
        
    def sym_decrypt(self, data): #decrypts the data
        plaintext_b64 = FR.decrypt(data)
        return(base64.b64decode(plaintext_b64).decode())
        
    def gen_asym_keys(self):
        self.private_key = rsa.generate_private_key(public_exponent=65537,key_size=4096,backend=default_backend())
        self.public_key = self.private_key.public_key() 
        self.private_pem = self.private_key.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.TraditionalOpenSSL,encryption_algorithm=serialization.NoEncryption())
        self.public_pem = self.public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
        #The code first generates the private key, then it converts that into a PEM string with the encoding of serialization.Encoding.PEM, 
        #format of serialization.PrivateFormat.TraditionalOpenSSL, encryption algorithm of serialization.NoEncryption(), 
        #and finally it creates the public key from this PEM string with the encoding of serialization.Encoding.PEM, 
        #format of serialization.PublicFormat.SubjectPublicKeyInfo().
    def import_key(self, data):
        self.client_key = load_pem_public_key(data, backend=default_backend())

    def asym_encrypt(self, data):
        return(self.client_key.encrypt(data,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None)))

    def asym_decrypt(self, data):
        return(self.private_key.decrypt(data,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None)))

    #the code above imports the client_key, which is a PEM public key file.
    #Then it creates an asym_encrypt function that encrypts data with the client_key using OAEP padding.
    #It then creates an asym_decrypt function that decrypts data with the private key using OAEP padding.

    def server_exchange(self): #after the connection the server exchanges keys with the client
        self.printmessage("Exchanging keys with client")
        while True:
            self.conn.send(self.public_pem)
            data = self.conn.recv(10240).decode()
            if "-----BEGIN PUBLIC KEY-----" in data:
                self.import_key(data.encode('utf-8'))
                break
            else:
                pass
        aes_key = self.asym_encrypt(sym_key)
        self.conn.send(aes_key)
        self.printmessage("Exchanged keys with client")
 
    def client_exchange(self): #client exchanges keys with the server
        self.printmessage("Exchanging keys with server")
        while True:
            data = self.conn.recv(10240).decode()
            if "-----BEGIN PUBLIC KEY-----" in data:
                self.import_key(data.encode('utf-8'))
                self.conn.send(self.public_pem)
                break
            else:
                pass
        while True:
            data = self.conn.recv(10240)
            if len(data) > 10:
                aes_key = self.asym_decrypt(data)
                self.gen_sym_key(aes_key)
                self.conn.send("===OK===".encode('utf-8'))
                self.printmessage("Exchanged keys with server")
                break
            else:
                pass

    def checkstr(self, data):
        outstr = ""
        if "===MSG===" in data:
            for ln in data.split("\n"):
                if "===MSG===" in ln:
                    pass
                else:
                    outstr += ln
            return self.sym_decrypt(outstr.encode())
        else:
            return "1"
    
    def printmessage(self, sender, msg = None):
        prmsg = '{}: {}\n'.format(sender, msg) if msg is not None else sender + '\n'
        self.cwindow.configure(state='normal')
        self.cwindow.insert(INSERT, prmsg)
        self.cwindow.configure(state='disabled')
        print(prmsg)
    
    def recv(self):
        data = self.conn.recv(10240)
        if "MSG" in data.decode():
            msg = self.sym_decrypt(data.decode().split("|||")[1].encode('utf-8'))
            self.printmessage("REC", msg)
        else:
            pass
               
    def chat(self, msg):
                
        cyphertext = "MSG|||{}".format(self.sym_encrypt(msg).decode()).encode('utf-8')
        self.conn.send(cyphertext)
        self.printmessage("SND", msg)
