from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from optparse import OptionParser
import sys, os
from os import chdir
from shutil import copyfile
import requests
from uuid import uuid4
from selenium.common.exceptions import TimeoutException

		
def query_webpage_statuscode(host,url,timeout):
	try:
		r = requests.head(host+url,timeout=timeout)
		return (r.status_code)
	except Exception as e :
		print (e)
		print ("failed on " + host + url)
		
def screenshot(host,url,file_name, driver):
	if verbose:
		print ("attempting to screenshot: " + str(url))
	try:
		driver.get(host+url)
		print(file_name)
		driver.save_screenshot(file_name)
		return True
	except TimeoutException:
		if verbose:
			print ("Failed to screenshot: "+ str(e))
		return False


def dirp(host ,URLS, outpath, timeout=10,extension="", verbose=True ,user_agent="Mozilla/5.0 (Windows NT\6.1) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/41.0.2228.\0 Safari/537.36"):
	outpath = os.path.join(outpath, "output")
	imagesOutputPath = os.path.join(outpath, "images")
	if not os.path.exists(outpath):
		os.makedirs(outpath)
	if not os.path.exists(imagesOutputPath):
		os.makedirs(imagesOutputPath)
	
	print ("Starting on " + host)
	
	queue = []
	queue.append(host)
	
	dcap = dict(DesiredCapabilities.PHANTOMJS)
	dcap["phantomjs.page.settings.userAgent"] = user_agent
	dcap["accept_untrusted_certs"] = True
	driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'], desired_capabilities=dcap) # or add to your PATH
	driver.set_window_size(1024, 768) # optional
	driver.set_page_load_timeout(timeout)
	
	#If these status codes are returned from a HEAD, a screenshot is attempted.
	found_codes = [200,301]
	#if these status codes are returned, it is assumed a directory.
	not_found_codes = [403]
	
	if not os.path.exists(outpath):
		os.makedirs(outpath)
		
	while (queue):
		base = queue.pop(0)
		#host = host + base #Take the next root URL

		for url in URLS:
			if (extension is not None):
				url = url + str(extension)
			if verbose:
				print ("Querying " + host + url)
			statuscode = query_webpage_statuscode(host,url,timeout)
			if verbose:
				print ("Status Code: "+ str(statuscode))

			if (statuscode in found_codes):
				print ("found " + url)
				filename = os.path.join("output", "images", str(url + str(uuid4()))  + ".png")
				if verbose:
					if (screenshot(host,url,filename,driver)):
						print ("Successful screenshot: " + str(host) + str(url))
					else:
						print ("Unsuccessful screenshot: "+ str(host) + str(url))
			elif (statuscode in not_found_codes):
				if verbose:
					print ("Found directory: " + str(url))
				queue.append(host+url+"/") #append a found directory

	
	
			
	


if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option("-f", "--file", action="store", dest="filename",
					  help="Wordlist containing directories", metavar="FILE")
	parser.add_option("-i", "--ip", action="store", dest="host",
					  help="Host to scan. Provided as an IP. Append a base directory for the root folder. i.e. https://192.168.1.1/root/to/scan")
	parser.add_option("-u", '--user-agent', action='store', 
					  dest="user_agent", type=str, 
					  default="Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML,\
							  like Gecko) Chrome/41.0.2228.0 Safari/537.36", 
					  help='The user agent used for requests')
	parser.add_option("-t", '--timeout', action='store', 
					  dest="timeout", type=int, default=10, 
					  help='Number of seconds to try to resolve')
	parser.add_option("-v", action='store_true', dest="verbose",
					  help='Adds some verbosity when running.')
	parser.add_option("-x", action='store', dest="extension",
					  help='extension to append. i.e. .jsp, .html, .aspx')
					  


	(options, args) = parser.parse_args()
	timeout = options.timeout
	verbose = options.verbose
	user_agent = options.user_agent
	extension = options.extension
	if options.filename:
		with open(options.filename, 'r') as inputFile:
			if verbose:
				print ("Using " +options.filename)
			URLS = inputFile.readlines()
			URLS = map(lambda s: s.strip(), URLS)
	else:
		print("No valid wordlist provided.")
		sys.exit()
		
	if options.host:
		host = options.host
		if not host.startswith("http://") and not host.startswith("https://"):
			print ("Provide a host with a valid HTTP or HTTPS prefix i.e. http:// or https://")
			sys.exit()
	
			


	if verbose:
		print("timeout: "+ str(timeout))
		print("verbose: "+ str(verbose))
		print("user_agent: "+ str(user_agent))
		print("extension: "+ str(extension))



		
	

	dirp(host, URLS, os.getcwd(), timeout, extension, verbose, user_agent)
