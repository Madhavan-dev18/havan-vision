import { useEffect, useRef, useState } from "react";
import * as faceapi from "@vladmandic/face-api";
import { Brain, Camera, CameraOff } from "lucide-react";

export default function WebcamScanner({ onEmotionDetected }) {
  const videoRef = useRef(null);
  const [isInitializing, setIsInitializing] = useState(true);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [currentEmotion, setCurrentEmotion] = useState("neutral");

  useEffect(() => {
    const loadModels = async () => {
      try {
        // We use the reliable unpkg CDN for the modern weights to avoid downloading 20MB of files manually
        const MODEL_URL = "https://unpkg.com/@vladmandic/face-api/model/";
        await Promise.all([
          faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
          faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL),
        ]);
        setIsInitializing(false);
      } catch (error) {
        console.error("Error loading face models:", error);
      }
    };
    loadModels();
  }, []);

  const startVideo = () => {
    navigator.mediaDevices
      .getUserMedia({ video: { width: 320, height: 240 } })
      .then((stream) => {
        let video = videoRef.current;
        if (video) {
          video.srcObject = stream;
          video.play();
          setIsCameraActive(true);
        }
      })
      .catch((err) => console.error("Error accessing webcam:", err));
  };

  const stopVideo = () => {
    let video = videoRef.current;
    if (video && video.srcObject) {
      video.srcObject.getTracks().forEach((track) => track.stop());
      setIsCameraActive(false);
    }
  };

  const handleVideoPlay = () => {
    setInterval(async () => {
      if (videoRef.current && isCameraActive) {
        const detections = await faceapi
          .detectSingleFace(videoRef.current, new faceapi.TinyFaceDetectorOptions())
          .withFaceExpressions();

        if (detections) {
          // Sort expressions by highest probability
          const expressions = detections.expressions;
          const dominant = Object.keys(expressions).reduce((a, b) =>
            expressions[a] > expressions[b] ? a : b
          );
          
          if (dominant !== currentEmotion) {
            setCurrentEmotion(dominant);
            // Send the emotion up to the Chat page
            if (onEmotionDetected) onEmotionDetected(dominant);
          }
        }
      }
    }, 1000); // Scan every 1 second to save CPU
  };

  return (
    <div className="bg-ink border border-azure-800 rounded-xl p-4 flex flex-col items-center shadow-soft">
      <div className="flex items-center justify-between w-full mb-3">
        <h3 className="text-azure-100 text-sm font-semibold flex items-center gap-2">
          <Brain size={16} className="text-azure-400" />
          Visual Cortex
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
          <div className="text-azure-400/50 text-xs animate-pulse">Loading AI Core...</div>
        ) : !isCameraActive ? (
          <div className="text-azure-400/50 text-xs">Camera Offline</div>
        ) : null}
        
        <video
          ref={videoRef}
          onPlay={handleVideoPlay}
          className={`w-full h-full object-cover transform -scale-x-100 ${!isCameraActive ? 'hidden' : ''}`}
          muted
        />
      </div>

      {isCameraActive && (
        <div className="mt-3 text-xs text-azure-200 bg-azure-900/50 px-3 py-1 rounded-full capitalize">
          Detected: <span className="font-bold text-azure-400">{currentEmotion}</span>
        </div>
      )}
    </div>
  );
}