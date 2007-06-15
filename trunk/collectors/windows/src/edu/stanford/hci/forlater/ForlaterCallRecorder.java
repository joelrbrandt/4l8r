package edu.stanford.hci.forlater;
import com.skype.Call;
import com.skype.CallAdapter;
import com.skype.CallStatusChangedListener;
import com.skype.Skype;
import com.skype.SkypeException;

import java.io.*;
import java.net.MalformedURLException;
import java.text.*;
import java.util.*;

import javax.sound.sampled.AudioFileFormat;
import javax.sound.sampled.AudioFormat;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.DataLine;
import javax.sound.sampled.LineUnavailableException;
import javax.sound.sampled.TargetDataLine;

public class ForlaterCallRecorder {
	static PrintWriter callLog;
	static final String CALL_LOG_COLUMN_SEPARATOR = "<>";

	public static final int LENGTH_BEGINNING_PAUSE = 750;
	public static final int LENGTH_RECOGNIZED_OUTGOING = 4000; // actually 3.72780s
	public static final String RECOGNIZED_GREETING_URI = "file:///c:/diary/vm/outgoing/outgoing_recognized.wav";
	public static final int LENGTH_UNRECOGNIZED_OUTGOING = 5250; // actually 5.00871
	public static final String UNRECOGNIZED_GREETING_URI = "file:///c:/diary/vm/outgoing/outgoing_unrecognized.wav";

	public static final String DIRECTORY_INCOMING = "c:\\diary\\vm\\incoming\\";
	public static final String DIRECTORY_FINAL = "c:\\diary\\vm\\";
	public static final SimpleDateFormat DATE_FORMAT_FOR_FILE = 
		new SimpleDateFormat("yyyyMMdd_HHmmss");
	public static final SimpleDateFormat DATE_FORMAT_FOR_LOG = 
		new SimpleDateFormat("MM/dd/yyyy HH:mm:ss");

	private void playSound(String file){
		java.applet.AudioClip clip;
		try {
			clip = java.applet.Applet.newAudioClip(new java.net.URL(file));
			clip.play();
		} catch (MalformedURLException e) {
			e.printStackTrace();
		}
	}

	void log(String msg) {
		try {
			// Open up the output file
			callLog = new PrintWriter(new BufferedWriter(new FileWriter(DIRECTORY_INCOMING + "callLog.txt",true)));
			callLog.println(msg);
			callLog.close();
		}
		catch (IOException ignored) {} 
	}

	public ForlaterCallRecorder() throws SkypeException {

		Skype.setDebug(false);
		Skype.addCallListener(new CallAdapter() {
			@Override
			public void callReceived(Call call) throws SkypeException {
				final Date startTime = new Date();
				final String incomingCallNumber = call.getPartnerId();
				final Call incomingCall = call;
				final String filePrefix = DATE_FORMAT_FOR_FILE.format(startTime) + "_" + (incomingCallNumber.length() > 10 ? incomingCallNumber.substring(incomingCallNumber.length() - 10) : incomingCallNumber);
				final String filename = DIRECTORY_INCOMING + filePrefix + ".wav";
				final SimpleAudioRecorder recorder = getNewRecorder(filename); 

				call.addCallStatusChangedListener(new CallStatusChangedListener(){
					public void statusChanged(Call.Status status) throws SkypeException {
						System.out.println(status);

						if (status == Call.Status.RINGING){

							// Start recording
							// incomingCall.redirectOutputToFile(filename);

							incomingCall.answer();

							Date start;

							// pause for just a brief moment after answering so skype gets goin'
							start = new Date();
							while (true){
								try {
									Thread.sleep(10);
								} catch (InterruptedException e) {
									e.printStackTrace();
								}
								Date now = new Date();
								if ((now.getTime() - start.getTime()) > LENGTH_BEGINNING_PAUSE) break;
							}


							// boolean known = KNOWN_NUMBERS.contains(incomingCallNumber.substring(incomingCallNumber.length()-10, incomingCallNumber.length()));
							boolean known = true;
							if (known) {
								System.out.println("we know the number");
							}
							// this spawns a separate thread (doesn't block) to play the sound
							playSound(known ? RECOGNIZED_GREETING_URI : UNRECOGNIZED_GREETING_URI);

							// Wait for audio file to finish playing, roughly
							start = new Date();
							while (true){
								try {
									Thread.sleep(10);
								} catch (InterruptedException e) {
									e.printStackTrace();
								}
								Date now = new Date();
								if ((now.getTime() - start.getTime()) > (known ? LENGTH_RECOGNIZED_OUTGOING : LENGTH_UNRECOGNIZED_OUTGOING)) break;
							}

							// Beep using DTMF (key tones)
							incomingCall.send(Call.DTMF.TYPE_1);

							// pause for just a brief moment to get the tone overwith
							start = new Date();
							while (true){
								try {
									Thread.sleep(10);
								} catch (InterruptedException e) {
									e.printStackTrace();
								}
								Date now = new Date();
								if ((now.getTime() - start.getTime()) > LENGTH_BEGINNING_PAUSE) break;
							}
							
							// actually start the recording
							recorder.start();

						}
						else if (status == Call.Status.FINISHED) {
							recorder.stopRecording();

							Date endTime = new Date();
							log(incomingCallNumber + CALL_LOG_COLUMN_SEPARATOR +
									DATE_FORMAT_FOR_LOG.format(startTime) + CALL_LOG_COLUMN_SEPARATOR +
									DATE_FORMAT_FOR_LOG.format(endTime));
							(new LameRunner(DIRECTORY_INCOMING + filePrefix + ".wav",
									DIRECTORY_FINAL + filePrefix + ".mp3",
									ForlaterCallRecorder.this)).start();
						}
					}
				});

				System.out.println("Called by: " + call.getPartnerId());

				System.out.println("callReceived() end");
			}

		});
	}

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		System.out.println("Starting up the Skype Call Recorder...");

		try {
			new ForlaterCallRecorder();
		} catch (SkypeException se) {
			se.printStackTrace();
		}

		System.out.println("...running!");
		while(true) {
			try {		
				Thread.sleep(10000);
			}
			catch (InterruptedException e) {}
		}
	}

	public SimpleAudioRecorder getNewRecorder(String filename) {

		File outputFile = new File(filename);

		AudioFormat	audioFormat = new AudioFormat(
				AudioFormat.Encoding.PCM_SIGNED,
				44100.0F, 16, 2, 4, 44100.0F, false);

		DataLine.Info info = new DataLine.Info(TargetDataLine.class, audioFormat);
		TargetDataLine targetDataLine = null;
		try
		{
			targetDataLine = (TargetDataLine) AudioSystem.getLine(info);
			targetDataLine.open(audioFormat);
		}
		catch (LineUnavailableException e)
		{
			System.out.println("Error: Unable to get a recording line");
			e.printStackTrace();
			return null;
		}

		AudioFileFormat.Type targetType = AudioFileFormat.Type.WAVE;

		SimpleAudioRecorder	recorder = new SimpleAudioRecorder(
				targetDataLine,
				targetType,
				outputFile);

		return recorder;

	}

}

class LameRunner extends Thread {
	private String inFile, outFile;
	private ForlaterCallRecorder cr;

	public LameRunner(String inFile, String outFile, ForlaterCallRecorder cr) {
		this.inFile = inFile;
		this.outFile = outFile;
		this.cr = cr;
	}

	public void run() {
		Process proc = null;
		System.out.println("Starting encoding of " + outFile);
		String[] procArgs = { "c:\\lame\\lame.exe", "-b", "48", "--resample", "22.05", "--quiet", inFile, outFile };
		try {
			proc = Runtime.getRuntime().exec(procArgs);
		} catch (IOException e) {
			e.printStackTrace();
		}

		if (proc != null) {
			InputStream is = proc.getInputStream();
			byte[] buf = new byte[100];
			while (true) {
				try {
					if (is.read(buf) < 0)
						break;
				} catch (IOException e) {
					// TODO Auto-generated catch block
					break;
				}
			}
		}

		if (proc != null) {
			cr.log("Completed encoding " + outFile + " with exit code " + proc.exitValue());
			System.out.println("Finished encoding of " + outFile + " with exit code " + proc.exitValue());
		}
		else {
			cr.log("Could not create process to encode " + outFile);
			System.out.println("Error: could not create process to encode " + outFile);
		}


	}

}