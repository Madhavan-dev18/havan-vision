import { useEffect, useRef, useState } from "react";
import * as faceapi from "@vladmandic/face-api";
import { Brain, Camera, CameraOff } from "lucide-react";

export default function WebcamScanner({ onEmotionDetected }) {
  const videoRef = useRef(null);
  const timeoutRef = useRef(null);
  const isActiveRef = useRef(false); // FIXED: Ref to avoid stale closure
  const [isInitializing, setIsInitializing] = useState(true);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [currentEmotion, setCurrentEmotion] = useState("neutral");

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
          isActiveRef.current = true; // Sync ref with state
        }
      })
      .catch((err) => console.error("Error accessing webcam:", err));
  };

  const stopVideo = () => {
    let video = videoRef.current;
    if (video && video.srcObject) {
      video.srcObject.getTracks().forEach((track) => track.stop());
    }
    setIsCameraActive(false);
    isActiveRef.current = false; // Instantly break the loop
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  };

  const handleVideoPlay = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);

    const scanFrame = async () => {
      // FIXED: Use ref to check active status to avoid the stale closure bug
      if (!isActiveRef.current || !videoRef.current) return;

      try {
        const detections = await faceapi
          .detectSingleFace(videoRef.current, new faceapi.TinyFaceDetectorOptions())
          .withFaceExpressions();

        if (detections) {
          const expressions = detections.expressions;
          const dominant = Object.keys(expressions).reduce((a, b) =>
            expressions[a] > expressions[b] ? a : b
          );

          setCurrentEmotion((prev) => {
            if (prev !== dominant) {
              if (onEmotionDetected) onEmotionDetected(dominant);
              return dominant;
            }
            return prev;
          });
        }
      } catch (err) {
        console.warn("Frame scan failed:", err);
      }

      timeoutRef.current = setTimeout(scanFrame, 1000);
    };

    scanFrame();
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