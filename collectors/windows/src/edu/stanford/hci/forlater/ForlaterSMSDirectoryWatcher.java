package edu.stanford.hci.forlater;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;

public class ForlaterSMSDirectoryWatcher extends AbstractDirectoryWatcher {

	private static final String SMS_EXTENSION = ".sms";


	public ForlaterSMSDirectoryWatcher(File directory, File doneDirectory) {
		super(directory, doneDirectory, new String[] { SMS_EXTENSION });
	}

	@Override
	public boolean processFile(File f) {
		ForlaterProcessor.log("Processing SMS file: " + f.getName());
		String from = null;
		String body = null;
		boolean result = false;
		
		
		try { // parse the file
			FileReader fr = new FileReader(f);
			char cbuf[] = new char[32768];
			int count = fr.read(cbuf);
			String header = (new String(cbuf)).substring(0, count);
			String[] lines = header.split("[\r\n]+");
			for (String s : lines) {
				if (s.startsWith("Sender=")) {
					from = s.substring(s.indexOf("=") + 1);
					if (from.length() > 10) {
						from = from.substring(from.length() - 10, from.length());
					}
				} else if (s.startsWith("Data=")) {
					body = s.substring(s.indexOf("=") + 1);
				}
			}
			fr.close();
		} catch (FileNotFoundException e) {
			ForlaterProcessor.log("Error processing header: " + e.getMessage());
		} catch (IOException e) {
			ForlaterProcessor.log("Error processing header: " + e.getMessage());
		}

		if (from != null) {
			System.out.println("From: \"" + from + "\"");
		}
		if (body != null) {
			System.out.println("Body: \"" + body + "\"");
		}

		if (from != null && body != null) {
			result = ForlaterProcessor.addEntry(from, body, null, null);
		}

		return result;
	}


}
