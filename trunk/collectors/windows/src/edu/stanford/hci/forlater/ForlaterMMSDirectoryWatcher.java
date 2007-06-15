package edu.stanford.hci.forlater;


import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;

public class ForlaterMMSDirectoryWatcher extends AbstractDirectoryWatcher {

	private static final String MMS_EXTENSION = ".hdr";
	public static final SimpleDateFormat DATE_FORMAT_FOR_FILE = 
		new SimpleDateFormat("yyyyMMdd_HHmmss");

	public ForlaterMMSDirectoryWatcher(File directory, File doneDirectory) {
		super(directory, doneDirectory, new String[] { MMS_EXTENSION });
	}

	@Override
	public boolean processFile(File f) {
		ForlaterProcessor.log("Processing MMS file: " + f.getName());
		String from = null;
		String subject = null;
		String body = null;
		boolean result = false;
		
		ArrayList<File> files = new ArrayList<File>();
		File pictureFile = null;

		try { // parse the file
			FileReader fr = new FileReader(f);
			char cbuf[] = new char[32768];
			int count = fr.read(cbuf);
			String header = (new String(cbuf)).substring(0, count);
			String[] lines = header.split("[\r\n]+");
			for (String s : lines) {
				if (s.startsWith("From: ")) {
					from = s.substring(s.indexOf(": ") + 2, s.indexOf("/"));
					if (from.length() > 10) {
						from = from.substring(from.length() - 10, from.length());
					}
				} else if (s.startsWith("Subject: ")) {
					subject = s.substring(s.indexOf(": ") + 2);
				} else if (s.startsWith("X-NowMMS-Content-Location: ")) {
					files.add(new File(this.getDirectory().getAbsolutePath() + File.separator + s.substring(s.indexOf(": ") + 2)));
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
		if (subject != null) {
			System.out.println("Subject: \"" + subject + "\"");
		}

		for (File fi : files) {
			String filename = fi.getName().toLowerCase();
			if (filename.endsWith(".jpg") || filename.endsWith(".jpeg")) {
				System.out.println("Picture (JPEG): \"" + fi.getAbsolutePath() + "\"");
				pictureFile = fi;
			} else if (filename.endsWith(".txt") || filename.endsWith(".text")) {
				System.out.println("Text: \"" + fi.getAbsolutePath() + "\"");
				FileReader fr;
				try {
					fr = new FileReader(fi);
					char cbuf[] = new char[32768];
					int count = fr.read(cbuf);
					String content = (new String(cbuf)).substring(0, count);
					content = content.replaceAll("[\r]+", "");
					if (body != null) {
						body = body + "\n" + content;
					} else {
						body = content;
					}
					fr.close();
				} catch (FileNotFoundException e) {
					ForlaterProcessor.log("Error processing included file " + fi.getName() + ": " + e.getMessage());
				} catch (IOException e) {
					ForlaterProcessor.log("Error processing included file " + fi.getName() + ": " + e.getMessage());
				}
			} else {
				System.out.println("Unknown File: \"" + fi.getAbsolutePath() + "\"");
			}
		}

		if (body != null) {
			System.out.println("Body: \"" + body + "\"");
		}

		String text = "";
		if (body != null || subject != null) {
			if (subject != null) text = text + subject;
			if (body != null) {
				if (subject != null) text = text + "\n";
				text = text + body;
			}
		}

		if (text.length() == 0) {
			text = null;
		}

		if (from != null && (text != null || pictureFile != null)) {
			result = ForlaterProcessor.addEntry(from, text, null, pictureFile);
		}

		return result;
	}

}
