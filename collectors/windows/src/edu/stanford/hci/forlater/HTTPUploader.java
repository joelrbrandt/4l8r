package edu.stanford.hci.forlater;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.HttpStatus;
import org.apache.commons.httpclient.methods.PostMethod;
import org.apache.commons.httpclient.methods.multipart.FilePart;
import org.apache.commons.httpclient.methods.multipart.MultipartRequestEntity;
import org.apache.commons.httpclient.methods.multipart.Part;
import org.apache.commons.httpclient.methods.multipart.StringPart;
import org.apache.commons.httpclient.params.HttpMethodParams;

public class HTTPUploader {

	public static boolean doPost(String targetURL, List<Part> fileParts, String authToken) {

		boolean result = false;
		
		PostMethod filePost = new PostMethod(targetURL);
		filePost.getParams().setBooleanParameter(HttpMethodParams.USE_EXPECT_CONTINUE, true);
		
		
		try {
			filePost.setRequestEntity(new MultipartRequestEntity(fileParts.toArray(new Part[0]), filePost.getParams()));
			filePost.setRequestHeader("Cookie", "auth_token=" + authToken);
			
			
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
		ArrayList<Part> parts = new ArrayList<Part>();
		File f = new File("c:\\bar.txt");
		try {
			parts.add(new FilePart("myfile", "foo.txt", f));
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		}
		parts.add(new StringPart("mymsg", "does \" all & this % get \' escaped ; correctly\n?"));
		HTTPUploader.doPost("https://www.4l8r.org/hello/upload", parts, "asdf");
	}

}
