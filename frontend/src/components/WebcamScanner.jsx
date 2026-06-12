import { useEffect, useRef, useState } from "react";
import * as faceapi from "@vladmandic/face-api";
import { Brain, Camera, CameraOff, Activity } from "lucide-react";

export default function WebcamScanner({ onEmotionDetected }) {
  const videoRef = useRef(null);
  const timeoutRef = useRef(null);
  const isActiveRef = useRef(false);
  
  const emotionBuffer = useRef([]); 
  
  const [isInitializing, setIsInitializing] = useState(true);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [currentEmotion, setCurrentEmotion] = useState("neutral");

  // TELEMETRY HUD
  const [faceDetected, setFaceDetected] = useState(false);
  const [rawScores, setRawScores] = useState({});

  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      isActiveRef.current = false;
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  useEffect(() => {
    const loadModels = async () => {
      try {
        const MODEL_URL = "https://unpkg.com/@vladmandic/face-api/model/";
        // UPGRADE: Swapping the weak Tiny model for the highly accurate SSD MobileNet V1
        await Promise.all([
          faceapi.nets.ssdMobilenetv1.loadFromUri(MODEL_URL),
          faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL),
        ]);
        setIsInitializing(false);
      } catch (error) {
        console.error("Error loading heavy face models:", error);
      }
    };
    loadModels();
  }, []);

 const startVideo = () => {
    navigator.mediaDevices
      .getUserMedia({ 
        video: { 
          width: { ideal: 1280 },  // Demand HD resolution
          height: { ideal: 720 }, 
          facingMode: "user"       // Explicitly request the front-facing camera
        } 
      })
      .then((stream) => {
        let video = videoRef.current;
        if (video) {
          video.srcObject = stream;
          video.play();
          setIsCameraActive(true);
          isActiveRef.current = true;
        }
      })
      .catch((err) => {
        console.error("Error accessing high-res webcam:", err);
        // Fallback if the user has a literal potato for a camera
        alert("Could not access HD webcam. Check permissions.");
      });
  };

  const stopVideo = () => {
    let video = videoRef.current;
    if (video && video.srcObject) {
      video.srcObject.getTracks().forEach((track) => track.stop());
    }
    setIsCameraActive(false);
    isActiveRef.current = false;
    setFaceDetected(false);
    setRawScores({});
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  };

  const handleVideoPlay = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);

    const scanFrame = async () => {
      if (!isActiveRef.current || !videoRef.current) return;

      try {
        // UPGRADE: Use SSD options with a low confidence threshold to force detection in bad environments
        const options = new faceapi.SsdMobilenetv1Options({ 
          minConfidence: 0.2 
        });

        const detections = await faceapi
          .detectSingleFace(videoRef.current, options)
          .withFaceExpressions();

        if (detections) {
          setFaceDetected(true);
          const expressions = detections.expressions;
          setRawScores(expressions); 

          let highestNonNeutralEmotion = "neutral";
          let highestNonNeutralScore = 0;

          for (const [emotion, score] of Object.entries(expressions)) {
            if (emotion !== "neutral" && score > highestNonNeutralScore) {
              highestNonNeutralScore = score;
              highestNonNeutralEmotion = emotion;
            }
          }

          let detectedEmotion = highestNonNeutralScore > 0.05 ? highestNonNeutralEmotion : "neutral";

          emotionBuffer.current.push(detectedEmotion);
          if (emotionBuffer.current.length > 5) {
            emotionBuffer.current.shift();
          }

          const nonNeutralFrames = emotionBuffer.current.filter(e => e !== "neutral");
          let outputEmotion = "neutral";
          
          if (nonNeutralFrames.length > 0) {
            const counts = {};
            let maxCount = 0;
            for (const e of nonNeutralFrames) {
              counts[e] = (counts[e] || 0) + 1;
              if (counts[e] > maxCount) {
                maxCount = counts[e];
                outputEmotion = e;
              }
            }
          }

          setCurrentEmotion((prev) => {
            if (prev !== outputEmotion) {
              if (onEmotionDetected) onEmotionDetected(outputEmotion);
              return outputEmotion;
            }
            return prev;
          });
        } else {
          setFaceDetected(false);
          setRawScores({});
        }
      } catch (err) {
        // Ignore expected dropped frames
      }

      timeoutRef.current = setTimeout(scanFrame, 200); 
    };

    scanFrame();
  };

  const formatScore = (val) => (val ? (val * 100).toFixed(1) : "0.0");

  return (
    <div className="bg-ink border border-azure-800 rounded-xl p-4 flex flex-col items-center shadow-soft">
      <div className="flex items-center justify-between w-full mb-3">
        <h3 className="text-azure-100 text-sm font-semibold flex items-center gap-2">
          <Brain size={16} className="text-azure-400" />
          Visual Cortex (SSD)
        </h3>
        <button
          onClick={isCameraActive ? stopVideo : startVideo}
          disabled={isInitializing}
          className={`p-2 rounded-full transition-colors ${
            isCameraActive ? "bg-red-500/20 text-red-400 hover:bg-red-500/30" : "bg-azure-500/20 text-azure-400 hover:bg-azure-500/30"
          } disabled:opacity-50`}
        >
          {isCameraActive ? <CameraOff size={16} /> : <Camera size={16} />}
        </button>
      </div>

      <div className="relative w-full aspect-video bg-black rounded-lg overflow-hidden flex items-center justify-center">
        {isInitializing ? (
          <div className="text-azure-400/50 text-xs animate-pulse text-center px-4">
            Loading Heavy SSD AI Core...<br/>(This takes longer)
          </div>
        ) : !isCameraActive ? (
          <div className="text-azure-400/50 text-xs">Camera Offline</div>
        ) : !faceDetected && isCameraActive ? (
          <div className="text-red-400/80 text-xs font-bold animate-pulse z-10 bg-black/60 px-3 py-1 rounded">No Face Detected</div>
        ) : null}

        <video
          ref={videoRef}
          onPlay={handleVideoPlay}
          className={`w-full h-full object-cover transform -scale-x-100 ${!isCameraActive ? 'hidden' : ''}`}
          muted
        />
      </div>

      {isCameraActive && (
        <div className="w-full mt-3 space-y-2">
          <div className="text-xs text-azure-200 bg-azure-900/50 px-3 py-2 rounded-lg flex items-center justify-between">
            <span>Locked Output:</span>
            <span className="font-bold text-azure-400 uppercase tracking-wider">{currentEmotion}</span>
          </div>

          <div className="bg-black/40 rounded-lg p-2.5 text-[10px] text-azure-300/70 font-mono">
            <div className="flex items-center gap-1.5 mb-1.5 border-b border-azure-800/50 pb-1.5">
              <Activity size={12} className="text-azure-400" /> SSD Neural Telemetry
            </div>
            <div className="grid grid-cols-2 gap-y-1 gap-x-2">
              <div className="text-azure-200">Neutral: {formatScore(rawScores.neutral)}%</div>
              <div className={rawScores.happy > 0.05 ? "text-green-400 font-bold" : ""}>Happy: {formatScore(rawScores.happy)}%</div>
              <div className={rawScores.sad > 0.05 ? "text-blue-400 font-bold" : ""}>Sad: {formatScore(rawScores.sad)}%</div>
              <div className={rawScores.angry > 0.05 ? "text-red-400 font-bold" : ""}>Angry: {formatScore(rawScores.angry)}%</div>
              <div className={rawScores.surprised > 0.05 ? "text-yellow-400 font-bold" : ""}>Surprise: {formatScore(rawScores.surprised)}%</div>
              <div className={rawScores.fear > 0.05 ? "text-purple-400 font-bold" : ""}>Fear: {formatScore(rawScores.fear)}%</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}