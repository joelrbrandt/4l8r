package edu.stanford.hci.forlater;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.channels.FileChannel;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;

import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.HttpStatus;
import org.apache.commons.httpclient.methods.PostMethod;
import org.apache.commons.httpclient.methods.multipart.FilePart;
import org.apache.commons.httpclient.methods.multipart.MultipartRequestEntity;
import org.apache.commons.httpclient.methods.multipart.Part;
import org.apache.commons.httpclient.methods.multipart.StringPart;
import org.apache.commons.httpclient.params.HttpMethodParams;

public class ForlaterProcessor {

	private static final String LOGFILE = "c:\\diary\\log.txt";
	public static final SimpleDateFormat DATE_FORMAT_FOR_LOG = 
		new SimpleDateFormat("MM/dd/yyyy HH:mm:ss");

	static final File SMS_DIRECTORY = new File("c:\\Program Files\\NowSMS\\SMS-IN");
	static final File SMS_DIRECTORY_PROCESSED = new File("c:\\Program Files\\NowSMS\\SMS-IN\\processed");
	
	static final File VM_DIRECTORY = new File("c:\\diary\\vm");
	static final File VM_DIRECTORY_PROCESSED = new File("c:\\diary\\vm\\processed");

	static final File MMS_DIRECTORY = new File("c:\\Program Files\\NowSMS\\MMS-IN");
	static final File MMS_DIRECTORY_PROCESSED = new File("c:\\Program Files\\NowSMS\\MMS-IN\\processed");
	
	private static final String UPLOAD_URL = "https://www.4l8r.org/a/upload";
	private static final String AUTH_TOKEN = "supersecret4l8r";
	
	public static boolean addEntry(String from, String text, File audioFile, File pictureFile) {
		
		if (from != null && from.length() == 0)
			from = null;
		
		if (text != null && text.length() == 0)
			text = null;
		
		if (from == null) {
			log("Error: can't add an entry without a \"from\" argument");
			return false;
		}
	
		if (text == null && audioFile == null && pictureFile == null) {
			log("Error: can't add an entry without a snippet");
			return false;
		}
		
		if (doPost(from, text, audioFile, pictureFile)) {
			log("Success posting entry!");
			return true;
		}
		else {
			log("Error: unknown error posting entry -- will try again");
			return false;
		}
	}

	static void log(String msg) {
		msg = "[" + DATE_FORMAT_FOR_LOG.format(new Date()) + "] " + msg;
		System.out.println("LOG: " + msg);
		PrintWriter log = null;
		try {
			// Open up the output file
			log = new PrintWriter(new BufferedWriter(new FileWriter(LOGFILE)));
			log.println(msg);
			log.close();
		}
		catch (IOException ioe) {
			System.out.println("LOG: ERROR WRITING TO LOG: " + ioe.getMessage());
		} 
	}

	public static void copyFile(File in, File out) throws Exception {
		FileChannel sourceChannel = new FileInputStream(in).getChannel();
		FileChannel destinationChannel = new FileOutputStream(out).getChannel();
		sourceChannel.transferTo(0, sourceChannel.size(), destinationChannel);
		sourceChannel.close();
		destinationChannel.close();
	}

	public static boolean doPost(String from, String text, File audioFile, File pictureFile) {

		boolean result = false;
			
		PostMethod filePost = new PostMethod(UPLOAD_URL);
		filePost.getParams().setBooleanParameter(HttpMethodParams.USE_EXPECT_CONTINUE, true);
		
		try {
			ArrayList<Part> parts = new ArrayList<Part>();
			
			if (from != null)
				parts.add(new StringPart("from", from));
			
			if (text != null)
				parts.add(new StringPart("text", text));
			
			if (audioFile != null) 
				parts.add(new FilePart("audioFile", audioFile.getName(), audioFile));
			
			if (pictureFile != null)
				parts.add(new FilePart("pictureFile", pictureFile.getName(), pictureFile));
			
			
			filePost.setRequestEntity(new MultipartRequestEntity(parts.toArray(new Part[0]), filePost.getParams()));
			
			filePost.setRequestHeader("Cookie", "auth_token=" + AUTH_TOKEN);
			
			
			HttpClient client = new HttpClient();
			
			client.getHttpConnectionManager().getParams().setConnectionTimeout(5000);
			int status = client.executeMethod(filePost);
			if (status == HttpStatus.SC_OK) {
				System.out.println("Upload complete, response=" + filePost.getResponseBodyAsString());
				result = true;
			} else {
				System.out.println("Upload failed, response=" + HttpStatus.getStatusText(status));
			}
		} catch (Exception ex) {
			System.out.println("ERROR: " + ex.getClass().getName() + " "+ ex.getMessage());
			ex.printStackTrace();
		} finally {
			filePost.releaseConnection();
		}
		
		return result;
	}
	
	
	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		System.out.println("Starting up the Mobile Diary Collector...");

		System.out.println("  bringing up the incoming voicemail watcher...");
		(new ForlaterVMDirectoryWatcher(VM_DIRECTORY, VM_DIRECTORY_PROCESSED)).start();
		System.out.println("  ...done");

		System.out.println("  bringing up the incoming SMS watcher...");
		(new ForlaterSMSDirectoryWatcher(SMS_DIRECTORY, SMS_DIRECTORY_PROCESSED)).start();
		System.out.println("  ...done");

		System.out.println("  bringing up the incoming MMS watcher...");
		(new ForlaterMMSDirectoryWatcher(MMS_DIRECTORY, MMS_DIRECTORY_PROCESSED)).start();
		System.out.println("  ...done");

		System.out.println("...running!");
		while(true) {
			try {		
				Thread.sleep(1000);
			}
			catch (InterruptedException e) {}
		}
	}
}
