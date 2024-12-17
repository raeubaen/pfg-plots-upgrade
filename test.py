import os, sys, urllib.request, urllib.error, urllib.parse, http.client, json
import ROOT
import array


serverurl = 'https://cmsweb.cern.ch/dqm/offline'
ident = "DQMToJson/1.0 python/%d.%d.%d" % sys.version_info[:3]
HTTPS = http.client.HTTPSConnection

class X509CertAuth(HTTPS):
 ssl_key_file = None
 ssl_cert_file = None

 def __init__(self, host, *args, **kwargs):
   HTTPS.__init__(self, host,
                  key_file = X509CertAuth.ssl_key_file,
                  cert_file = X509CertAuth.ssl_cert_file,
                  **kwargs)

class X509CertOpen(urllib.request.AbstractHTTPHandler):
 def default_open(self, req):
   return self.do_open(X509CertAuth, req)

def x509_params():
 key_file = cert_file = None

 x509_path = os.getenv("X509_USER_PROXY", None)
 if x509_path and os.path.exists(x509_path):
   key_file = cert_file = x509_path

 if not key_file:
   x509_path = os.getenv("X509_USER_KEY", None)
   if x509_path and os.path.exists(x509_path):
     key_file = x509_path

 if not cert_file:
   x509_path = os.getenv("X509_USER_CERT", None)
   if x509_path and os.path.exists(x509_path):
     cert_file = x509_path

 if not key_file:
   x509_path = os.getenv("HOME") + "/.globus/userkey.pem"
   if os.path.exists(x509_path):
     key_file = x509_path

 if not cert_file:
   x509_path = os.getenv("HOME") + "/.globus/usercert.pem"
   if os.path.exists(x509_path):
     cert_file = x509_path

 if not key_file or not os.path.exists(key_file):
   print("no certificate private key file found", file=sys.stderr)
   sys.exit(1)

 if not cert_file or not os.path.exists(cert_file):
   print("no certificate public key file found", file=sys.stderr)
   sys.exit(1)

 print(("Using SSL private key", key_file))
 print(("Using SSL public key", cert_file))
 return key_file, cert_file


def dqm_get_json(server, run, dataset, folder, plotname):
 X509CertAuth.ssl_key_file, X509CertAuth.ssl_cert_file = x509_params()

 path = f"jsrootfairy/archive/{run}/{dataset}/{folder}/{urllib.parse.quote(plotname)}"
 path = path.replace("//", "/")
 url = f"{server}/{path}"

 print(url)

 datareq = urllib.request.Request(url)
 datareq.add_header('User-agent', ident)

 buildopener = urllib.request.build_opener(X509CertOpen())
 return buildopener.open(datareq).read().decode("utf-8")


if __name__ == "__main__":
 #/jsonfairy/archive/387506/StreamExpress/Run2024J-Express-v1/DQMIO/EcalBarrel/EBSummaryClient/EBTMT timing mean 1D summary
 run = '387474'
 dataset = '/StreamExpress/Run2024J-Express-v1/DQMIO/'
 folder = 'EcalBarrel/EBSummaryClient/'
 plotname = "EBTMT timing mean 1D summary"
 data = dqm_get_json(serverurl, run, dataset, folder, plotname)

 #print(data)

 h = ROOT.TBufferJSON.ConvertFromJSON(str(data))
 h.Print()
 h.Draw()
