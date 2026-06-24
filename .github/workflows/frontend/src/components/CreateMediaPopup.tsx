import React, { useState } from "react";
import avatars from "@/data/avatars.json";
import voices from "@/data/voices.json";
import languages from "@/data/languages.json";

interface MediaConfig {
  avatarId: string;
  voiceId: string;
  language: string;
  tone: string;
  script: string;
  facialExpressions: boolean;
  eyeMovement: boolean;
  blinking: boolean;
  headMovement: boolean;
}

interface CreateMediaPopupProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (config: MediaConfig) => void;
}

export default function CreateMediaPopup({
  isOpen,
  onClose,
  onSubmit,
}: CreateMediaPopupProps) {
  const [config, setConfig] = useState<MediaConfig>({
    avatarId: avatars.avatars[0].id,
    voiceId: voices.voices[0].id,
    language: "en-US",
    tone: "professional",
    script: "",
    facialExpressions: true,
    eyeMovement: true,
    blinking: true,
    headMovement: true,
  });

  const selectedAvatar = avatars.avatars.find(
    (a) => a.id === config.avatarId
  );
  const selectedVoice = voices.voices.find((v) => v.id === config.voiceId);
  const selectedLanguage = languages.languages.find(
    (l) => l.code === config.language
  );

  const handleSubmit = () => {
    if (!config.script.trim()) {
      alert("Please enter a script");
      return;
    }
    onSubmit(config);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 flex justify-between items-center sticky top-0">
          <h2 className="text-2xl font-bold">Create AI Video</h2>
          <button
            onClick={onClose}
            className="text-white hover:bg-blue-800 rounded p-2 text-xl"
          >
            X
          </button>
        </div>

        <div className="p-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left: Selectors */}
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-3">
                  Choose Avatar (Realistic, No Dead Eyes)
                </h3>
                <div className="grid grid-cols-3 gap-3">
                  {avatars.avatars.map((avatar) => (
                    <button
                      key={avatar.id}
                      onClick={() =>
                        setConfig({ ...config, avatarId: avatar.id })
                      }
                      className={`p-3 rounded-lg border-2 transition ${
                        config.avatarId === avatar.id
                          ? "border-blue-600 bg-blue-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      <div className="w-full h-20 bg-gradient-to-br from-blue-400 to-blue-600 rounded mb-2 flex items-center justify-center text-white text-2xl">
                        👤
                      </div>
                      <p className="text-sm font-medium">{avatar.name}</p>
                      <p className="text-xs text-gray-500">Natural eyes</p>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-3">Tone</h3>
                <div className="grid grid-cols-2 gap-2">
                  {["professional", "friendly", "energetic", "calm"].map(
                    (tone) => (
                      <button
                        key={tone}
                        onClick={() => setConfig({ ...config, tone })}
                        className={`py-2 px-4 rounded border transition ${
                          config.tone === tone
                            ? "border-blue-600 bg-blue-100 text-blue-900 font-semibold"
                            : "border-gray-300 hover:border-gray-400"
                        }`}
                      >
                        {tone.charAt(0).toUpperCase() + tone.slice(1)}
                      </button>
                    )
                  )}
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-3">
                  Voice (ElevenLabs)
                </h3>
                <select
                  value={config.voiceId}
                  onChange={(e) =>
                    setConfig({ ...config, voiceId: e.target.value })
                  }
                  className="w-full p-3 border-2 border-gray-300 rounded-lg focus:border-blue-600 focus:outline-none"
                >
                  {voices.voices.map((voice) => (
                    <option key={voice.id} value={voice.id}>
                      {voice.name} - {voice.tone}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-3">Language</h3>
                <select
                  value={config.language}
                  onChange={(e) =>
                    setConfig({ ...config, language: e.target.value })
                  }
                  className="w-full p-3 border-2 border-gray-300 rounded-lg focus:border-blue-600 focus:outline-none"
                >
                  {languages.languages.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                      {lang.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <h4 className="font-semibold mb-3 text-green-900">
                  Facial Expression Settings
                </h4>
                <label className="flex items-center gap-2 mb-2">
                  <input
                    type="checkbox"
                    checked={config.facialExpressions}
                    onChange={(e) =>
                      setConfig({
                        ...config,
                        facialExpressions: e.target.checked,
                      })
                    }
                  />
                  <span className="text-sm">Facial Expressions</span>
                </label>
                <label className="flex items-center gap-2 mb-2">
                  <input
                    type="checkbox"
                    checked={config.eyeMovement}
                    onChange={(e) =>
                      setConfig({ ...config, eyeMovement: e.target.checked })
                    }
                  />
                  <span className="text-sm font-semibold">
                    Eye Movement (No Dead Eyes)
                  </span>
                </label>
                <label className="flex items-center gap-2 mb-2">
                  <input
                    type="checkbox"
                    checked={config.blinking}
                    onChange={(e) =>
                      setConfig({ ...config, blinking: e.target.checked })
                    }
                  />
                  <span className="text-sm">Natural Blinking</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={config.headMovement}
                    onChange={(e) =>
                      setConfig({ ...config, headMovement: e.target.checked })
                    }
                  />
                  <span className="text-sm">Head Movement</span>
                </label>
              </div>
            </div>

            {/* Right: Script & Preview */}
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-3">Script</h3>
                <textarea
                  value={config.script}
                  onChange={(e) =>
                    setConfig({ ...config, script: e.target.value })
                  }
                  placeholder="Enter your script. Avatar will use natural facial expressions and eye movement to match the tone..."
                  className="w-full h-40 p-4 border-2 border-gray-300 rounded-lg focus:border-blue-600 focus:outline-none resize-none"
                />
                <p className="text-sm text-gray-500 mt-2">
                  Recommended: 100-500 words for best results
                </p>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg border-2 border-gray-200">
                <h4 className="font-semibold mb-3">Selection Summary</h4>
                <div className="space-y-2 text-sm">
                  <p>
                    <span className="font-medium">Avatar:</span>{" "}
                    {selectedAvatar?.name}
                  </p>
                  <p>
                    <span className="font-medium">Voice:</span>{" "}
                    {selectedVoice?.name}
                  </p>
                  <p>
                    <span className="font-medium">Language:</span>{" "}
                    {selectedLanguage?.name}
                  </p>
                  <p>
                    <span className="font-medium">Tone:</span> {config.tone}
                  </p>
                  <p>
                    <span className="font-medium">Words:</span>{" "}
                    {config.script
                      .split(" ")
                      .filter((w) => w.length > 0).length}
                  </p>
                  <p className="text-xs text-green-600 mt-2">
                    ✓ Realistic facial expressions enabled
                  </p>
                  <p className="text-xs text-green-600">
                    ✓ Natural eye movement enabled
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="mt-8 flex gap-3 justify-end border-t pt-6">
            <button
              onClick={onClose}
              className="px-6 py-2 border-2 border-gray-300 rounded-lg hover:bg-gray-50 font-semibold"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              className="px-8 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
            >
              Generate Video
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
