import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { Sun, Moon, X } from "lucide-react";

export default function DekhoLanding() {
  const [isExpanded, setIsExpanded] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const modalRef = useRef(null);

  // Close modal when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (modalRef.current && !(modalRef.current as HTMLElement).contains(event.target as Node)) {
        setIsModalOpen(false);
      }
    };
    if (isModalOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isModalOpen]);

  // Video file names in the videos folder
  const videoFiles = ["model1.mp4", "model2.mp4"];

  return (
    <div
      className={`${
        darkMode
          ? "bg-gray-900 text-white"
          : "bg-gradient-to-br from-gray-100 to-gray-300 text-gray-900"
      } min-h-screen transition-colors duration-300 flex flex-col`}
    >
      <div className="p-4 flex justify-end">
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="p-3 rounded-full shadow-md bg-gray-800 text-white hover:bg-gray-700 transition flex items-center gap-2"
        >
          {darkMode ? (
            <Sun className="w-6 h-6 text-yellow-400" />
          ) : (
            <Moon className="w-6 h-6 text-blue-500" />
          )}
          <span className="hidden md:inline">
            {darkMode ? "Light Mode" : "Dark Mode"}
          </span>
        </button>
      </div>

      <section className="flex flex-col items-center justify-center text-center p-10 space-y-6 flex-grow">
        <motion.h1
          className="text-6xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-green-400"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
        >
          DEKHO: AI-Driven Traffic Management
        </motion.h1>
        <p className="text-lg max-w-3xl text-gray-300 dark:text-gray-700">
          Streamlining Traffic Congestion in a Priority-Based Manner
        </p>
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className="mt-4 px-8 py-4 bg-gradient-to-r from-blue-500 to-green-500 hover:from-blue-600 hover:to-green-600 rounded-xl text-lg font-bold shadow-lg transition"
          onClick={() => setIsModalOpen(true)}
        >
          Get Started
        </motion.button>
      </section>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <motion.div
            ref={modalRef}
            className="bg-white text-gray-900 p-6 rounded-2xl shadow-lg max-w-3xl w-full backdrop-blur-md bg-opacity-90"
            initial={{ opacity: 0, scale: 0.5 }} // Start smaller
            animate={{ opacity: 1, scale: 1 }} // Expand to full size
            exit={{ opacity: 0, scale: 0.5 }} // Shrink when closing
            transition={{ type: "spring", stiffness: 100, damping: 20 }} // Spring animation
          >
            <div className="flex justify-between items-center border-b pb-2">
              <h2 className="text-xl font-bold">Explore DEKHO in Action</h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-2 rounded-full bg-gray-200 hover:bg-gray-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="mt-4 grid grid-cols-1 gap-6">
              {videoFiles.map((video, index) => (
                <video 
                  key={index} 
                  className="w-full max-w-4xl mx-auto rounded-lg shadow-lg" 
                  controls
                >
                  <source src={`/videos/${video}`} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              ))}
            </div>
          </motion.div>
        </div>
      )}

      <section className="p-10">
        <h2 className="text-4xl font-bold text-center text-blue-400">Key Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-8">
          {[
            {
              title: "AI-Powered Optimization",
              desc: "Smart traffic signals adjust dynamically.",
            },
            {
              title: "Real-Time Data Analysis",
              desc: "Monitors and manages congestion effectively.",
            },
            {
              title: "Emergency Priority",
              desc: "Prioritizes ambulances and emergency vehicles.",
            },
          ].map((feature, index) => (
            <motion.div
              key={index}
              className={`p-6 rounded-2xl shadow-lg text-center transform hover:scale-105 transition ${
                darkMode
                  ? "bg-gray-800 backdrop-blur-md bg-opacity-90"
                  : "bg-gray-200 text-gray-900 backdrop-blur-md bg-opacity-90"
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <h3 className="text-xl font-semibold text-green-400 dark:text-green-700">
                {feature.title}
              </h3>
              <p className="text-gray-400 dark:text-gray-700 mt-2">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Footer with "Made with ❤️ by Team-UNIT-13" */}
      <footer className="text-center py-6 text-sm text-gray-400 dark:text-gray-500">
        Made with ❤️ by Team UNIT-13
      </footer>
    </div>
  );
}