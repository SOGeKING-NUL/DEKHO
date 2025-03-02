import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sun, Moon, X, ChevronDown, AlertTriangle, BarChart3, Clock, Car, Zap, Github, Star } from "lucide-react";

export default function DekhoLanding() {
    const [darkMode, setDarkMode] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [activeFeature, setActiveFeature] = useState(0);
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

    // Auto-rotate features
    useEffect(() => {
        const interval = setInterval(() => {
            setActiveFeature((prev) => (prev + 1) % 3);
        }, 5000);
        return () => clearInterval(interval);
    }, []);

    // Video file names in the videos folder
    const videoFiles = ["model1.mp4", "model2.mp4", "model3.mp4", "model4.mp4"];

    const features = [
        {
            title: "Emergency Priority",
            desc: "Intelligent system that automatically prioritizes ambulances and emergency vehicles to save critical minutes.",
            icon: <AlertTriangle className="w-10 h-10" />,
            color: "from-rose-500 to-pink-600"
        },
        {
            title: "Real-Time Data Analysis",
            desc: "Advanced algorithms monitor and manage congestion effectively, reducing wait times by up to 40%.",
            icon: <BarChart3 className="w-10 h-10" />,
            color: "from-cyan-500 to-blue-600"
        },
        {
            title: "AI-Powered Optimization",
            desc: "Smart traffic signals adjust dynamically based on real-time traffic patterns and density analysis.",
            icon: <Zap className="w-10 h-10" />,
            color: "from-purple-500 to-indigo-600"
        },
    ];

    return (
        <div
            className={`${darkMode
                    ? "bg-gradient-to-br from-gray-900 via-indigo-950 to-gray-900 text-white"
                    : "bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 text-gray-900"
                } min-h-screen transition-colors duration-500 flex flex-col`}
        >
            {/* Animated background elements */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                {[...Array(6)].map((_, i) => (
                    <motion.div
                        key={i}
                        className={`absolute rounded-full ${darkMode ? "bg-indigo-600" : "bg-indigo-300"
                            } bg-opacity-10 blur-3xl`}
                        initial={{
                            width: Math.random() * 300 + 100,
                            height: Math.random() * 300 + 100,
                            x: Math.random() * window.innerWidth,
                            y: Math.random() * window.innerHeight,
                            opacity: 0.1
                        }}
                        animate={{
                            x: Math.random() * window.innerWidth,
                            y: Math.random() * window.innerHeight,
                            opacity: [0.1, 0.2, 0.1]
                        }}
                        transition={{
                            duration: 15 + Math.random() * 20,
                            repeat: Infinity,
                            repeatType: "reverse"
                        }}
                    />
                ))}
            </div>

            {/* Header with theme toggle and GitHub button */}
            <header className="relative z-10 p-6 flex justify-between items-center">
                <motion.div
                    className="flex items-center gap-2"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5 }}
                >
                </motion.div>

                <div className="flex items-center gap-4">
                    {/* GitHub Star Button */}
                    <motion.a
                        href="https://github.com/Karush2807/DEKHO"
                        target="_blank"
                        rel="noopener noreferrer"
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.5, delay: 0.1 }}
                        className={`px-4 py-2 rounded-full shadow-lg flex items-center gap-2 ${darkMode
                                ? "bg-gray-800 text-white hover:bg-gray-700 border border-gray-700"
                                : "bg-white text-gray-900 hover:bg-gray-100 border border-gray-200"
                            } transition-all duration-300`}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        <Github className="w-5 h-5" />
                        <Star className="w-4 h-4 fill-current text-yellow-400" />
                        <span className="font-medium">Star</span>
                    </motion.a>

                    {/* Dark/Light Mode Toggle */}
                    <motion.button
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.5 }}
                        onClick={() => setDarkMode(!darkMode)}
                        className={`relative w-14 h-7 rounded-full shadow-lg transition-all duration-300 ${darkMode
                                ? "bg-gradient-to-r from-indigo-800 to-purple-900"
                                : "bg-gradient-to-r from-blue-300 to-purple-300"
                            }`}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        <motion.div
                            className={`absolute top-1 w-5 h-5 rounded-full flex items-center justify-center ${darkMode
                                    ? "bg-indigo-400 left-1"
                                    : "bg-white left-8"
                                } transition-all duration-300`}
                        >
                            {darkMode ? (
                                <Moon className="w-3 h-3 text-indigo-900" />
                            ) : (
                                <Sun className="w-3 h-3 text-yellow-500" />
                            )}
                        </motion.div>
                    </motion.button>
                </div>
            </header>

            {/* Hero Section */}
            <section className="relative z-10 flex flex-col items-center justify-center text-center px-6 py-16 md:py-24 space-y-8 flex-grow">
                <motion.div
                    initial={{ opacity: 0, y: -30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="space-y-4"
                >
                    <h1 className="text-6xl md:text-8xl font-bold">
                        <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600">
                            DEKHO
                        </span>
                    </h1>
                    <p className="text-2xl md:text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-500">
                        AI-Driven Traffic Management
                    </p>
                    <p className={`text-lg max-w-2xl mx-auto ${darkMode ? "text-gray-300" : "text-gray-600"}`}>
                        Revolutionizing urban mobility with intelligent traffic systems that prioritize emergency vehicles and optimize flow in real-time.
                    </p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.4 }}
                    className="flex flex-col sm:flex-row gap-4 mt-8"
                >
                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 rounded-xl text-lg font-bold shadow-lg transition-all duration-300"
                        onClick={() => setIsModalOpen(true)}
                    >
                        See It In Action
                    </motion.button>

                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className={`px-8 py-4 rounded-xl text-lg font-bold shadow-lg transition-all duration-300 ${darkMode
                                ? "bg-gray-800 hover:bg-gray-700 text-white border border-gray-700"
                                : "bg-white hover:bg-gray-100 text-gray-900 border border-gray-200"
                            }`}
                        onClick={() => {
                            const featuresSection = document.getElementById('features');
                            featuresSection?.scrollIntoView({ behavior: 'smooth' });
                        }}
                    >
                        Explore Features
                    </motion.button>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 1, delay: 1 }}
                    className="absolute bottom-10 left-1/2 transform -translate-x-1/2 animate-bounce"
                >
                    <ChevronDown className="w-8 h-8 opacity-70" />
                </motion.div>
            </section>

            {/* MODAL */}
            <AnimatePresence>
                {isModalOpen && (
                    <motion.div
                        className="fixed inset-0 bg-black bg-opacity-70 backdrop-blur-sm flex items-center justify-center z-50"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                    >
                        <motion.div
                            ref={modalRef}
                            className={`${darkMode
                                    ? "bg-gradient-to-br from-gray-900 to-indigo-950 border border-indigo-800"
                                    : "bg-white border border-indigo-100"
                                } p-6 rounded-2xl shadow-2xl max-w-5xl w-full mx-4`}
                            initial={{ opacity: 0, scale: 0.5, y: 50 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.5, y: 50 }}
                            transition={{ type: "spring", stiffness: 300, damping: 30 }}
                        >
                            <div className="flex justify-between items-center border-b pb-4 mb-6 border-opacity-20 border-indigo-300">
                                <h2 className={`text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500`}>
                                    DEKHO in Action
                                </h2>
                                <motion.button
                                    whileHover={{ scale: 1.1, rotate: 90 }}
                                    whileTap={{ scale: 0.9 }}
                                    onClick={() => setIsModalOpen(false)}
                                    className={`p-2 rounded-full ${darkMode
                                            ? "bg-indigo-900/50 hover:bg-indigo-800/70"
                                            : "bg-indigo-100 hover:bg-indigo-200"
                                        } transition-all duration-300`}
                                >
                                    <X className="w-5 h-5" />
                                </motion.button>
                            </div>

                            {/* Video Grid Layout */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {videoFiles.map((video, index) => (
                                    <motion.div
                                        key={index}
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ duration: 0.5, delay: index * 0.1 }}
                                        className="w-full"
                                    >
                                        <div className={`p-1.5 rounded-xl ${darkMode
                                                ? "bg-gradient-to-r from-blue-500 to-purple-600"
                                                : "bg-gradient-to-r from-blue-400 to-purple-500"
                                            } shadow-lg`}>
                                            <video
                                                className="w-full rounded-lg aspect-video object-cover"
                                                controls
                                            >
                                                <source src={`/videos/${video}`} type="video/mp4" />
                                                Your browser does not support the video tag.
                                            </video>
                                        </div>
                                        <div className={`mt-3 text-center ${darkMode ? "text-indigo-300" : "text-indigo-700"} font-medium`}>
                                            {index === 0 && "AI Traffic Analysis"}
                                            {index === 1 && "Emergency Vehicle Priority"}
                                            {index === 2 && "Congestion Management"}
                                            {index === 3 && "Real-time Optimization"}
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Key Features Section */}
            <section id="features" className="relative z-10 px-6 py-20">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    viewport={{ once: true }}
                    className="text-center mb-16"
                >
                    <h2 className="text-4xl md:text-5xl font-bold">
                        <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
                            Key Features
                        </span>
                    </h2>
                    <p className={`mt-4 max-w-2xl mx-auto ${darkMode ? "text-gray-300" : "text-gray-600"}`}>
                        Our cutting-edge technology transforms traffic management with these powerful capabilities
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
                    {features.map((feature, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                            viewport={{ once: true }}
                            whileHover={{ y: -10, scale: 1.02 }}
                            className={`p-6 rounded-2xl shadow-xl ${darkMode
                                    ? "bg-gradient-to-br from-gray-800/50 to-indigo-950/30 backdrop-blur-md border border-indigo-900/50"
                                    : "bg-gradient-to-br from-white/80 to-indigo-50/50 backdrop-blur-md border border-indigo-100"
                                } ${index === activeFeature ? "ring-2 ring-blue-500" : ""} transition-all duration-300`}
                        >
                            <div className={`w-20 h-20 mb-6 rounded-2xl bg-gradient-to-br ${feature.color} flex items-center justify-center mx-auto shadow-lg transform -rotate-3`}>
                                {feature.icon}
                            </div>
                            <h3 className="text-xl font-bold mb-3 text-center bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
                                {feature.title}
                            </h3>
                            <p className={`${darkMode ? "text-indigo-200" : "text-indigo-900"} text-center`}>
                                {feature.desc}
                            </p>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* Stats Section */}
            <section className="relative z-10 px-6 py-16 bg-gradient-to-r from-blue-500/10 to-purple-600/10">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    viewport={{ once: true }}
                    className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8"
                >
                    {[
                        { value: "40%", label: "Reduced Wait Time", icon: <Clock className="w-6 h-6" /> },
                        { value: "60%", label: "Less Congestion", icon: <Car className="w-6 h-6" /> },
                        { value: "3.5min", label: "Emergency Response", icon: <AlertTriangle className="w-6 h-6" /> }
                    ].map((stat, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, scale: 0.8 }}
                            whileInView={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                            viewport={{ once: true }}
                            whileHover={{ scale: 1.05 }}
                            className={`p-8 rounded-xl text-center ${darkMode
                                    ? "bg-gradient-to-br from-indigo-900/30 to-purple-900/20 backdrop-blur-sm border border-indigo-800/30"
                                    : "bg-gradient-to-br from-white/70 to-indigo-50/50 backdrop-blur-sm border border-indigo-100"
                                } shadow-lg`}
                        >
                            <div className="flex justify-center mb-4">
                                <div className={`w-16 h-16 rounded-full flex items-center justify-center ${darkMode ? "bg-gradient-to-br from-blue-500/30 to-purple-600/30" : "bg-gradient-to-br from-blue-100 to-indigo-100"
                                    } shadow-inner`}>
                                    {stat.icon}
                                </div>
                            </div>
                            <h3 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500 mb-2">
                                {stat.value}
                            </h3>
                            <p className={`${darkMode ? "text-indigo-200" : "text-indigo-700"} font-medium`}>
                                {stat.label}
                            </p>
                        </motion.div>
                    ))}
                </motion.div>
            </section>

            {/* Footer */}
            <footer className="relative z-10 py-10 text-center">
                <div className={`max-w-6xl mx-auto px-6 ${darkMode ? "text-indigo-300" : "text-indigo-700"}`}>
                    <motion.div
                        initial={{ opacity: 0 }}
                        whileInView={{ opacity: 1 }}
                        transition={{ duration: 1 }}
                        viewport={{ once: true }}
                        className="p-6 rounded-xl bg-gradient-to-r from-blue-500/5 to-purple-600/5"
                    >
                        <p className="text-lg mb-2 font-medium">Made with ❤️ by Team UNIT-13</p>
                        <p className="text-sm">© 2025 DEKHO - Revolutionizing Traffic Management</p>
                    </motion.div>
                </div>
            </footer>
        </div>
    );
}