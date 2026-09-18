const { useState, useEffect } = React;

const API_BASE = window.location.origin.includes(':8000') ? '' : 'http://127.0.0.1:8000';

// Các chủ đề gợi ý sẵn (Từ Golden Set)
const SUGGESTIONS = [
  {
    title: "Cửa sổ ngữ cảnh của LLM",
    topic: "Cửa sổ ngữ cảnh của mô hình ngôn ngữ",
    learning_goal: "Giải thích vì sao trợ lý AI quên phần đầu cuộc trò chuyện dài",
    audience: "Sinh viên năm nhất, chưa học lập trình",
    duration: 3,
  },
  {
    title: "Phân biệt AI, ML & Deep Learning",
    topic: "Học máy là gì",
    learning_goal: "Phân biệt được sự khác nhau giữa AI, Machine Learning và Deep Learning",
    audience: "Người mới bắt đầu tìm hiểu công nghệ",
    duration: 4,
  },
  {
    title: "Vì sao AI tự tin trả lời sai",
    topic: "Hiện tượng ảo giác (Hallucination) của AI",
    learning_goal: "Nhận ra 3 dấu hiệu thông tin sai và cách người dùng kiểm chứng",
    audience: "Người đi làm sử dụng AI hàng ngày",
    duration: 5,
  }
];

function App() {
  const [step, setStep] = useState(1);
  const [backendOnline, setBackendOnline] = useState(null);
  const [session, setSession] = useState(null);
  const [sources, setSources] = useState([]);
  const [script, setScript] = useState(null);

  // Kiểm tra kết nối backend khi mở app
  useEffect(() => {
    fetch(`${API_BASE}/`)
      .then(res => res.json())
      .then(data => {
        if (data.service) setBackendOnline(true);
      })
      .catch(() => setBackendOnline(false));
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      {/* Top Navigation */}
      <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center font-heading font-extrabold text-white text-xl shadow-lg shadow-indigo-500/20">
              S
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-heading font-bold text-lg text-white tracking-wide">ScriptScout</span>
                <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  Track C3 · Lesson Studio
                </span>
              </div>
              <p className="text-xs text-slate-400">Agent tự tìm tài liệu web & viết kịch bản video có dẫn nguồn</p>
            </div>
          </div>

          {/* Server Status Indicator */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs">
            <span className={`w-2 h-2 rounded-full ${backendOnline === true ? 'bg-emerald-400 animate-pulse' : backendOnline === false ? 'bg-rose-500' : 'bg-amber-400'}`}></span>
            <span className="text-slate-300 font-medium">
              {backendOnline === true ? 'Backend Online (Port 8000)' : backendOnline === false ? 'Backend Offline (Hãy chạy server)' : 'Đang kết nối...'}
            </span>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-5xl w-full mx-auto px-4 py-8 flex flex-col">
        {/* Stepper Progress Bar */}
        <div className="mb-8">
          <div className="grid grid-cols-3 gap-2 sm:gap-4">
            {/* Step 1 */}
            <div className={`flex items-center gap-3 p-3 rounded-xl border transition-all ${
              step === 1 
                ? 'bg-indigo-500/10 border-indigo-500/40 text-indigo-300' 
                : step > 1 
                ? 'bg-slate-900 border-slate-800 text-emerald-400' 
                : 'bg-slate-900/40 border-slate-800/60 text-slate-500'
            }`}>
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm ${
                step === 1 
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30' 
                  : step > 1 
                  ? 'bg-emerald-500/20 text-emerald-400' 
                  : 'bg-slate-800 text-slate-500'
              }`}>
                {step > 1 ? '✓' : '1'}
              </div>
              <div className="hidden sm:block">
                <div className="text-xs font-semibold uppercase tracking-wider opacity-75">Bước 1</div>
                <div className="text-sm font-medium">Thiết lập & Tìm kiếm</div>
              </div>
            </div>

            {/* Step 2 */}
            <div className={`flex items-center gap-3 p-3 rounded-xl border transition-all ${
              step === 2 
                ? 'bg-indigo-500/10 border-indigo-500/40 text-indigo-300' 
                : step > 2 
                ? 'bg-slate-900 border-slate-800 text-emerald-400' 
                : 'bg-slate-900/40 border-slate-800/60 text-slate-500'
            }`}>
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm ${
                step === 2 
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30' 
                  : step > 2 
                  ? 'bg-emerald-500/20 text-emerald-400' 
                  : 'bg-slate-800 text-slate-500'
              }`}>
                {step > 2 ? '✓' : '2'}
              </div>
              <div className="hidden sm:block">
                <div className="text-xs font-semibold uppercase tracking-wider opacity-75">Bước 2</div>
                <div className="text-sm font-medium">Duyệt & Thẩm định nguồn</div>
              </div>
            </div>

            {/* Step 3 */}
            <div className={`flex items-center gap-3 p-3 rounded-xl border transition-all ${
              step === 3 
                ? 'bg-indigo-500/10 border-indigo-500/40 text-indigo-300' 
                : 'bg-slate-900/40 border-slate-800/60 text-slate-500'
            }`}>
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm ${
                step === 3 
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30' 
                  : 'bg-slate-800 text-slate-500'
              }`}>
                3
              </div>
              <div className="hidden sm:block">
                <div className="text-xs font-semibold uppercase tracking-wider opacity-75">Bước 3</div>
                <div className="text-sm font-medium">Kịch bản & Trích dẫn</div>
              </div>
            </div>
          </div>
        </div>

        {/* Dynamic Step Content */}
        {step === 1 && (
          <Step1Setup 
            onSearchComplete={(newSession, loadedSources) => {
              setSession(newSession);
              setSources(loadedSources);
              setStep(2);
            }} 
          />
        )}

        {step === 2 && (
          <Step2Sources
            session={session}
            initialSources={sources}
            onBack={() => setStep(1)}
            onScriptGenerated={(newScript) => {
              setScript(newScript);
              setStep(3);
            }}
          />
        )}

        {step === 3 && (
          <Step3Script
            session={session}
            scriptData={script}
            sources={sources}
            onBack={() => setStep(2)}
            onReset={() => {
              setSession(null);
              setSources([]);
              setScript(null);
              setStep(1);
            }}
          />
        )}
      </main>
    </div>
  );
}

// COMPONENT: BƯỚC 1 (THIẾT LẬP & TÌM KIẾM TÀI LIỆU)
function Step1Setup({ onSearchComplete }) {
  const [topic, setTopic] = useState("Học máy là gì");
  const [learningGoal, setLearningGoal] = useState("Phân biệt được AI, học máy và học sâu qua ví dụ thực tế");
  const [audience, setAudience] = useState("Người mới bắt đầu học AI");
  const [duration, setDuration] = useState(3);
  
  const [loading, setLoading] = useState(false);
  const [searchStatus, setSearchStatus] = useState("");
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [errorMsg, setErrorMsg] = useState("");

  const handleApplyPreset = (preset) => {
    setTopic(preset.topic);
    setLearningGoal(preset.learning_goal);
    setAudience(preset.audience);
    setDuration(preset.duration);
    setErrorMsg("");
  };

  const handleStartSearch = async (e) => {
    e.preventDefault();
    if (!topic.trim()) {
      setErrorMsg("Vui lòng nhập chủ đề bài học.");
      return;
    }
    setErrorMsg("");
    setLoading(true);
    setSearchStatus("Đang khởi tạo phiên làm việc...");
    setTimeElapsed(0);

    // Bắt đầu đếm thời gian
    const timer = setInterval(() => {
      setTimeElapsed(prev => prev + 1);
    }, 1000);

    try {
      // 1. Tạo session
      const createRes = await fetch(`${API_BASE}/api/sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: topic.trim(),
          learning_goal: learningGoal.trim(),
          audience: audience.trim(),
          duration_minutes: Number(duration),
        })
      });

      if (!createRes.ok) {
        throw new Error(`Không thể tạo phiên làm việc (Mã lỗi: ${createRes.status})`);
      }
      const newSession = await createRes.json();
      const sessionId = newSession.id;

      // 2. Kích hoạt tìm kiếm nguồn
      setSearchStatus("Agent đang tìm kiếm bài viết web qua Tavily...");
      const searchRes = await fetch(`${API_BASE}/api/sessions/${sessionId}/search`, {
        method: "POST"
      });

      if (!searchRes.ok) {
        throw new Error(`Không thể kích hoạt tìm kiếm (Mã lỗi: ${searchRes.status})`);
      }

      // 3. Polling kiểm tra trạng thái
      let isDone = false;
      let attempts = 0;
      const maxAttempts = 60; // 60 * 2s = 120s

      while (!isDone && attempts < maxAttempts) {
        await new Promise(r => setTimeout(r, 2500));
        attempts++;

        const checkRes = await fetch(`${API_BASE}/api/sessions/${sessionId}`);
        if (!checkRes.ok) continue;

        const currentSession = await checkRes.json();
        const st = currentSession.status;

        if (attempts <= 5) {
          setSearchStatus("Đang truy xuất nội dung các bài viết web...");
        } else if (attempts <= 15) {
          setSearchStatus("LLM đang đọc hiểu & chấm điểm tin cậy (Trust Scoring)...");
        } else {
          setSearchStatus("Đang phân tích và đối soát mâu thuẫn giữa các tài liệu...");
        }

        if (st === "sources_ready") {
          isDone = true;
          setSearchStatus("Hoàn tất! Đang tải danh sách nguồn đã thẩm định...");
          
          // Lấy danh sách nguồn
          const sourcesRes = await fetch(`${API_BASE}/api/sessions/${sessionId}/sources`);
          const sourcesData = sourcesRes.ok ? await sourcesRes.json() : [];

          clearInterval(timer);
          setTimeout(() => {
            onSearchComplete(currentSession, sourcesData);
          }, 800);
          return;
        }

        if (st === "error") {
          throw new Error(currentSession.error || "Agent gặp lỗi trong quá trình tìm kiếm & xử lý.");
        }
      }

      if (!isDone) {
        throw new Error("Quá thời gian chờ tìm kiếm nguồn. Vui lòng thử lại.");
      }

    } catch (err) {
      clearInterval(timer);
      setErrorMsg(err.message || "Đã xảy ra lỗi không xác định.");
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 p-6 sm:p-8 rounded-2xl border border-slate-800 relative overflow-hidden">
        <div className="max-w-2xl relative z-10">
          <h1 className="text-2xl sm:text-3xl font-heading font-bold text-white mb-2">
            Tạo Kịch Bản Bài Giảng Với Nguồn Dẫn Chứng
          </h1>
          <p className="text-slate-300 text-sm leading-relaxed">
            Nhập chủ đề video của bạn. Hệ thống Multi-Agent sẽ tự động nghiên cứu internet, trích xuất tài liệu uy tín, và thẩm định trước khi bắt đầu viết.
          </p>
        </div>
        <div className="absolute right-0 top-0 bottom-0 w-80 bg-gradient-to-l from-indigo-500/10 to-transparent pointer-events-none hidden sm:block"></div>
      </div>

      {/* Quick Suggestions Chips */}
      <div className="space-y-2">
        <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          💡 Chọn nhanh chủ đề mẫu (Golden Set):
        </label>
        <div className="flex flex-wrap gap-2">
          {SUGGESTIONS.map((s, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleApplyPreset(s)}
              disabled={loading}
              className="text-xs px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-indigo-950/60 border border-slate-800 hover:border-indigo-500/40 text-slate-300 hover:text-indigo-300 transition-all text-left flex items-center gap-1.5"
            >
              <span className="text-indigo-400">✦</span>
              <span>{s.title}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Setup Form */}
      <form onSubmit={handleStartSearch} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6 shadow-xl">
        {errorMsg && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm flex items-start gap-3">
            <span className="text-lg">⚠️</span>
            <div className="flex-1 font-medium">{errorMsg}</div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Topic */}
          <div className="space-y-2 md:col-span-2">
            <label className="block text-sm font-semibold text-slate-200">
              1. Chủ đề bài giảng <span className="text-indigo-400">*</span>
            </label>
            <input 
              type="text" 
              value={topic}
              onChange={e => setTopic(e.target.value)}
              disabled={loading}
              placeholder="Ví dụ: Học máy (Machine Learning) là gì"
              className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-white placeholder-slate-500 text-sm transition-all"
            />
          </div>

          {/* Learning Goal */}
          <div className="space-y-2 md:col-span-2">
            <label className="block text-sm font-semibold text-slate-200">
              2. Mục tiêu người học cần đạt được
            </label>
            <input 
              type="text" 
              value={learningGoal}
              onChange={e => setLearningGoal(e.target.value)}
              disabled={loading}
              placeholder="Ví dụ: Hiểu khái niệm cơ bản và phân biệt được AI, ML, Deep Learning"
              className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-white placeholder-slate-500 text-sm transition-all"
            />
          </div>

          {/* Audience */}
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-slate-200">
              3. Đối tượng người học
            </label>
            <input 
              type="text" 
              value={audience}
              onChange={e => setAudience(e.target.value)}
              disabled={loading}
              placeholder="Ví dụ: Người mới bắt đầu học AI / Sinh viên năm nhất"
              className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-white placeholder-slate-500 text-sm transition-all"
            />
          </div>

          {/* Duration */}
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-slate-200">
              4. Thời lượng video dự kiến
            </label>
            <select
              value={duration}
              onChange={e => setDuration(Number(e.target.value))}
              disabled={loading}
              className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-white text-sm transition-all"
            >
              <option value={2}>2 phút (~20-25 câu)</option>
              <option value={3}>3 phút (~30-35 câu - Khuyên dùng)</option>
              <option value={5}>5 phút (~50 câu)</option>
              <option value={8}>8 phút (~80 câu)</option>
            </select>
          </div>
        </div>

        {/* Loading / Status State */}
        {loading && (
          <div className="p-6 rounded-xl bg-indigo-950/20 border border-indigo-500/30 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-sm font-medium text-indigo-300">{searchStatus}</span>
              </div>
              <span className="text-xs font-mono text-slate-400 bg-slate-900 px-2 py-1 rounded-md border border-slate-800">
                {timeElapsed}s
              </span>
            </div>

            {/* Progress indicators */}
            <div className="grid grid-cols-3 gap-2 text-xs pt-2 border-t border-indigo-950/40">
              <div className="flex items-center gap-1.5 text-indigo-400 font-medium">
                <span>✓</span> <span>Tavily Search</span>
              </div>
              <div className={`flex items-center gap-1.5 ${timeElapsed > 6 ? 'text-indigo-400 font-medium' : 'text-slate-600'}`}>
                <span>{timeElapsed > 6 ? '✓' : '○'}</span> <span>Scrape Web</span>
              </div>
              <div className={`flex items-center gap-1.5 ${timeElapsed > 15 ? 'text-indigo-400 font-medium' : 'text-slate-600'}`}>
                <span>{timeElapsed > 15 ? '✓' : '○'}</span> <span>Trust Scoring</span>
              </div>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={loading}
            className={`w-full py-4 rounded-xl font-heading font-semibold text-base transition-all flex items-center justify-center gap-2 ${
              loading 
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed' 
                : 'bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white shadow-lg shadow-indigo-600/30 glow-effect'
            }`}
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-slate-400 border-t-transparent rounded-full animate-spin"></div>
                <span>Đang xử lý tài liệu...</span>
              </>
            ) : (
              <>
                <span>Bắt đầu Tìm kiếm & Thẩm định nguồn</span>
                <span className="text-lg">➔</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

// COMPONENT: BƯỚC 2 (DUYỆT & THẨM ĐỊNH NGUỒN)
function Step2Sources({ session, initialSources, onBack, onScriptGenerated }) {
  const [sources, setSources] = useState(initialSources || []);
  const [filter, setFilter] = useState("all"); // 'all' | 'active' | 'conflicts'
  const [expandedCodes, setExpandedCodes] = useState({});
  
  // State thêm nguồn thủ công
  const [customUrl, setCustomUrl] = useState("");
  const [addingSource, setAddingSource] = useState(false);
  const [addError, setAddError] = useState("");

  // State sinh kịch bản
  const [generating, setGenerating] = useState(false);
  const [genStatus, setGenStatus] = useState("");
  const [genElapsed, setGenElapsed] = useState(0);
  const [genError, setGenError] = useState("");

  const activeCount = sources.filter(s => s.is_active).length;
  const conflictCount = sources.filter(s => !!s.conflict_note).length;

  // Toggle Bật / Tắt nguồn
  const handleToggle = async (code, currentActive) => {
    const nextState = !currentActive;
    // Optimistic update
    setSources(prev => prev.map(s => s.code === code ? { ...s, is_active: nextState } : s));

    try {
      const res = await fetch(`${API_BASE}/api/sessions/${session.id}/sources/${code}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: nextState })
      });
      if (!res.ok) {
        throw new Error("Lỗi khi cập nhật trạng thái nguồn.");
      }
    } catch (err) {
      // Revert if error
      setSources(prev => prev.map(s => s.code === code ? { ...s, is_active: currentActive } : s));
      alert("Không thể lưu trạng thái nguồn: " + err.message);
    }
  };

  // Thêm nguồn tự chọn bằng URL
  const handleAddSource = async (e) => {
    e.preventDefault();
    const url = customUrl.trim();
    if (!url) return;
    if (!url.startsWith("http://") && !url.startsWith("https://")) {
      setAddError("URL không hợp lệ. Hãy nhập đường dẫn bắt đầu bằng http:// hoặc https://");
      return;
    }

    setAddError("");
    setAddingSource(true);
    try {
      const res = await fetch(`${API_BASE}/api/sessions/${session.id}/sources`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Không thể tải và phân tích URL này.");
      }

      const newSource = await res.json();
      setSources(prev => [newSource, ...prev]);
      setCustomUrl("");
    } catch (err) {
      setAddError(err.message || "Lỗi khi thêm nguồn.");
    } finally {
      setAddingSource(false);
    }
  };

  // Kích hoạt sinh kịch bản
  const handleGenerateScript = async () => {
    if (activeCount === 0) {
      setGenError("Vui lòng kích hoạt ít nhất 1 nguồn tài liệu để AI có căn cứ viết bài.");
      return;
    }

    setGenError("");
    setGenerating(true);
    setGenStatus("Script Agent đang lập cấu trúc kịch bản theo mục tiêu học...");
    setGenElapsed(0);

    const timer = setInterval(() => {
      setGenElapsed(prev => prev + 1);
    }, 1000);

    // Dynamic status text
    const statusInterval = setInterval(() => {
      setGenStatus(prev => {
        if (prev.includes("lập cấu trúc")) return "Đang phân rã từng câu nói và gán mã trích dẫn nguồn...";
        if (prev.includes("phân rã")) return "Verify Agent đang đối soát từng câu với tài liệu gốc...";
        return "Đang hoàn tất và đóng gói kịch bản video...";
      });
    }, 8000);

    try {
      const res = await fetch(`${API_BASE}/api/sessions/${session.id}/script`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Lỗi server (${res.status}) khi sinh kịch bản.`);
      }

      const scriptData = await res.json();
      clearInterval(timer);
      clearInterval(statusInterval);
      onScriptGenerated(scriptData);
    } catch (err) {
      clearInterval(timer);
      clearInterval(statusInterval);
      setGenError(err.message || "Không thể sinh kịch bản. Vui lòng thử lại.");
      setGenerating(false);
    }
  };

  const toggleExpand = (code) => {
    setExpandedCodes(prev => ({ ...prev, [code]: !prev[code] }));
  };

  const filteredSources = sources.filter(s => {
    if (filter === "active") return s.is_active;
    if (filter === "conflicts") return !!s.conflict_note;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Overview Top Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              Đang duyệt cho đề tài
            </span>
            <span className="text-xs text-slate-400">Thời lượng: {session?.duration_minutes || 3} phút</span>
          </div>
          <h2 className="text-xl font-heading font-bold text-white">{session?.topic || "Chủ đề bài giảng"}</h2>
          <p className="text-xs text-slate-400 mt-0.5">Mục tiêu: {session?.learning_goal}</p>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <div className="px-4 py-2 rounded-xl bg-slate-950 border border-slate-800 text-center flex-1 sm:flex-initial">
            <div className="text-xs text-slate-400">Nguồn đang bật</div>
            <div className="text-lg font-bold text-emerald-400 font-heading">
              {activeCount} <span className="text-xs text-slate-500 font-normal">/ {sources.length}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Add Custom Source & Filter Bar */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        {/* Filters */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-900 border border-slate-800 rounded-xl">
          <button
            onClick={() => setFilter("all")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              filter === "all" ? "bg-indigo-600 text-white shadow-sm" : "text-slate-400 hover:text-white"
            }`}
          >
            Tất cả ({sources.length})
          </button>
          <button
            onClick={() => setFilter("active")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              filter === "active" ? "bg-indigo-600 text-white shadow-sm" : "text-slate-400 hover:text-white"
            }`}
          >
            Đang bật ({activeCount})
          </button>
          <button
            onClick={() => setFilter("conflicts")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1 ${
              filter === "conflicts" ? "bg-amber-600 text-white shadow-sm" : "text-amber-400/80 hover:text-amber-300"
            }`}
          >
            <span>⚡ Mâu thuẫn</span>
            <span>({conflictCount})</span>
          </button>
        </div>

        {/* Add Source Input Form */}
        <form onSubmit={handleAddSource} className="flex-1 max-w-md flex items-center gap-2">
          <input
            type="url"
            value={customUrl}
            onChange={e => setCustomUrl(e.target.value)}
            disabled={addingSource}
            placeholder="Dán link bài viết bổ sung (https://...)"
            className="flex-1 px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 focus:border-indigo-500 text-xs text-white placeholder-slate-500"
          />
          <button
            type="submit"
            disabled={addingSource || !customUrl.trim()}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-medium border border-slate-700 disabled:opacity-50 flex items-center gap-1.5 whitespace-nowrap"
          >
            {addingSource ? (
              <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <span>+ Thêm nguồn</span>
            )}
          </button>
        </form>
      </div>

      {addError && (
        <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs">
          ⚠️ {addError}
        </div>
      )}

      {/* Sources List */}
      <div className="space-y-4">
        {filteredSources.length === 0 ? (
          <div className="p-12 text-center rounded-2xl bg-slate-900/60 border border-slate-800 text-slate-400">
            Không tìm thấy nguồn nào trong bộ lọc này.
          </div>
        ) : (
          filteredSources.map((source) => {
            const isExpanded = expandedCodes[source.code];
            const trust = Number(source.trust_score || 0.5);
            const trustPercent = Math.round(trust * 100);

            // Màu sắc theo điểm uy tín
            const badgeColor = trust >= 0.7 
              ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
              : trust >= 0.5
              ? "bg-amber-500/10 text-amber-400 border-amber-500/30"
              : "bg-rose-500/10 text-rose-400 border-rose-500/30";

            return (
              <div
                key={source.code}
                className={`rounded-2xl border transition-all overflow-hidden ${
                  source.is_active
                    ? "bg-slate-900 border-slate-800 hover:border-slate-700 shadow-md"
                    : "bg-slate-950/60 border-slate-850 opacity-60 grayscale-[40%]"
                }`}
              >
                <div className="p-5 sm:p-6 space-y-4">
                  {/* Card Header: Code, Title, Toggle */}
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3">
                      <span className="font-mono text-xs font-bold px-2 py-1 rounded-md bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 mt-0.5">
                        {source.code}
                      </span>
                      <div>
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-heading font-semibold text-base text-white hover:text-indigo-400 transition-colors flex items-center gap-1.5"
                        >
                          <span>{source.title || source.url}</span>
                          <span className="text-xs text-slate-500">↗</span>
                        </a>
                        <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400 mt-1">
                          <span className="text-slate-300 font-medium">🌐 {source.domain || "Web"}</span>
                          {source.author && <span>✍️ {source.author}</span>}
                          {source.published_date && <span>📅 {source.published_date}</span>}
                        </div>
                      </div>
                    </div>

                    {/* Toggle Switch */}
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <span className="text-xs text-slate-400 hidden sm:inline">
                        {source.is_active ? "Đang sử dụng" : "Đã loại bỏ"}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleToggle(source.code, source.is_active)}
                        className={`w-12 h-6 rounded-full transition-colors relative p-0.5 focus:outline-none ${
                          source.is_active ? "bg-indigo-600" : "bg-slate-800 border border-slate-700"
                        }`}
                        title={source.is_active ? "Bấm để loại bỏ nguồn này" : "Bấm để sử dụng nguồn này"}
                      >
                        <div
                          className={`w-5 h-5 rounded-full bg-white transition-transform ${
                            source.is_active ? "translate-x-6" : "translate-x-0"
                          }`}
                        />
                      </button>
                    </div>
                  </div>

                  {/* Trust Score & Reason */}
                  <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 text-xs">
                    <div className="sm:col-span-4 flex items-center gap-2.5">
                      <span className={`px-2.5 py-1 rounded-lg border font-bold ${badgeColor}`}>
                        {trustPercent}% Độ tin cậy
                      </span>
                      <div className="flex-1 bg-slate-800 h-2 rounded-full overflow-hidden hidden sm:block">
                        <div
                          className={`h-full rounded-full ${
                            trust >= 0.7 ? "bg-emerald-500" : trust >= 0.5 ? "bg-amber-500" : "bg-rose-500"
                          }`}
                          style={{ width: `${trustPercent}%` }}
                        />
                      </div>
                    </div>

                    <div className="sm:col-span-8 text-slate-300 flex items-center">
                      <p className="line-clamp-2">
                        <span className="text-slate-400 font-medium">Nhận xét AI:</span> {source.trust_reason || "Chưa có đánh giá chi tiết."}
                      </p>
                    </div>
                  </div>

                  {/* Conflict Alert (Nếu có mâu thuẫn số liệu) */}
                  {source.conflict_note && (
                    <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-start gap-2.5">
                      <span className="text-base flex-shrink-0">⚡</span>
                      <div>
                        <span className="font-bold">Mâu thuẫn thông tin phát hiện: </span>
                        <span>{source.conflict_note}</span>
                      </div>
                    </div>
                  )}

                  {/* Unverified Claims (Nếu có tuyên bố cần xác minh) */}
                  {source.unverified_claims && source.unverified_claims.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5 text-xs">
                      <span className="text-slate-500 text-[11px]">Cần kiểm chứng:</span>
                      {source.unverified_claims.map((claim, cIdx) => (
                        <span key={cIdx} className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/60 text-[11px]">
                          {claim}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Excerpt Snippet with Expand/Collapse */}
                  {source.excerpt && (
                    <div className="pt-2 border-t border-slate-800/80">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                          Đoạn trích nội dung trang web:
                        </span>
                        <button
                          onClick={() => toggleExpand(source.code)}
                          className="text-[11px] text-indigo-400 hover:text-indigo-300 font-medium"
                        >
                          {isExpanded ? "Thu gọn ▲" : "Xem thêm ▼"}
                        </button>
                      </div>
                      <p className={`text-xs text-slate-400 leading-relaxed font-mono bg-slate-950/60 p-3 rounded-lg border border-slate-850 ${
                        isExpanded ? "" : "line-clamp-2"
                      }`}>
                        {source.excerpt}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Error Message if Generation Fails */}
      {genError && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm flex items-start gap-3">
          <span className="text-lg">⚠️</span>
          <div className="flex-1 font-medium">{genError}</div>
        </div>
      )}

      {/* Action Footer */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4 sticky bottom-4 z-30 backdrop-blur-lg bg-slate-900/90 shadow-2xl">
        <button
          type="button"
          onClick={onBack}
          disabled={generating}
          className="px-5 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium transition-all w-full sm:w-auto"
        >
          ← Quay lại thiết lập
        </button>

        <div className="flex items-center gap-4 w-full sm:w-auto">
          <div className="text-xs text-right hidden sm:block">
            <div className="text-white font-semibold">{activeCount} nguồn đã chọn</div>
            <div className="text-slate-400">AI chỉ dùng các nguồn này để viết</div>
          </div>

          <button
            type="button"
            onClick={handleGenerateScript}
            disabled={generating || activeCount === 0}
            className={`px-8 py-3.5 rounded-xl font-heading font-semibold text-sm transition-all flex items-center justify-center gap-2 flex-1 sm:flex-initial ${
              generating || activeCount === 0
                ? "bg-slate-800 text-slate-500 cursor-not-allowed"
                : "bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white shadow-lg shadow-indigo-600/30 glow-effect"
            }`}
          >
            {generating ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Đang sinh kịch bản ({genElapsed}s)...</span>
              </>
            ) : (
              <>
                <span>Xác nhận nguồn & Sinh kịch bản</span>
                <span className="text-base">➔</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Generating Modal Overlay */}
      {generating && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center space-y-6 shadow-2xl glow-effect">
            <div className="w-16 h-16 mx-auto rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center">
              <div className="w-8 h-8 border-3 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
            </div>

            <div>
              <h3 className="text-xl font-heading font-bold text-white mb-2">Đang Biên Soạn Kịch Bản</h3>
              <p className="text-sm text-indigo-300 font-medium min-h-[40px] flex items-center justify-center">
                {genStatus}
              </p>
            </div>

            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs text-slate-400">
              Thời gian xử lý: <span className="font-mono text-white font-bold">{genElapsed}s</span> (khoảng 20-30s)
            </div>

            <p className="text-[11px] text-slate-500">
              Mọi câu chứa thông tin đều được trích dẫn mã nguồn và tự động đối soát trích dẫn gốc.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

// COMPONENT: BƯỚC 3 (KỊCH BẢN 2 CỘT SPLIT-VIEW & ĐỐI CHIẾU TRÍCH DẪN)
function Step3Script({ session, scriptData, sources, onBack, onReset }) {
  const script = scriptData?.json_content || scriptData || {};
  const sentences = script.cau || [];
  const sections = script.phan || [];
  const verification = script._verification_summary || {};
  
  // Nguồn map để tra cứu nhanh thông tin nguồn
  const sourceMap = React.useMemo(() => {
    const map = {};
    (sources || []).forEach(s => {
      map[s.code] = s;
    });
    return map;
  }, [sources]);

  // Câu đang được chọn để soi bằng chứng ở cột phải
  const [selectedN, setSelectedN] = useState(sentences[0]?.n || 1);
  const [filterType, setFilterType] = useState("all"); // 'all' | 'cited' | 'verified'
  const [exporting, setExporting] = useState(false);
  const [toastMsg, setToastMsg] = useState("");

  const showToast = (msg) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(""), 3000);
  };

  const selectedSentence = sentences.find(s => s.n === selectedN) || sentences[0];

  // Map section name
  const sectionMap = React.useMemo(() => {
    const map = {};
    sections.forEach(p => {
      map[p.so] = p.ten;
    });
    return map;
  }, [sections]);

  // Export Markdown handler
  const handleExportMarkdown = async () => {
    setExporting(true);
    try {
      const res = await fetch(`${API_BASE}/api/sessions/${session.id}/export?format=markdown`);
      if (!res.ok) throw new Error("Lỗi khi tải file Markdown");
      const text = await res.text();
      
      const blob = new Blob([text], { type: "text/markdown;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `kich_ban_${session?.topic ? session.topic.replace(/\s+/g, '_') : 'script'}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showToast("✅ Đã xuất file Markdown thành công!");
    } catch (err) {
      alert("Lỗi xuất Markdown: " + err.message);
    } finally {
      setExporting(false);
    }
  };

  // Export JSON handler
  const handleExportJSON = async () => {
    setExporting(true);
    try {
      const res = await fetch(`${API_BASE}/api/sessions/${session.id}/export?format=json`);
      if (!res.ok) throw new Error("Lỗi khi tải file JSON");
      const data = await res.json();
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `scriptscout_${session?.id || 'export'}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showToast("✅ Đã xuất file JSON thành công!");
    } catch (err) {
      alert("Lỗi xuất JSON: " + err.message);
    } finally {
      setExporting(false);
    }
  };

  // Copy Markdown to clipboard
  const handleCopyMarkdown = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/sessions/${session.id}/export?format=markdown`);
      if (!res.ok) throw new Error("Lỗi khi đọc file");
      const text = await res.text();
      await navigator.clipboard.writeText(text);
      showToast("📋 Đã sao chép toàn bộ kịch bản vào bộ nhớ tạm!");
    } catch (err) {
      alert("Không thể sao chép: " + err.message);
    }
  };

  const filteredSentences = sentences.filter(s => {
    if (filterType === "cited") return (s.nguon && s.nguon.length > 0);
    if (filterType === "verified") return s.citation_verified === true;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Toast alert */}
      {toastMsg && (
        <div className="fixed top-5 right-5 z-50 px-4 py-3 rounded-xl bg-emerald-600 text-white font-medium text-sm shadow-xl flex items-center gap-2 animate-bounce">
          <span>{toastMsg}</span>
        </div>
      )}

      {/* Script Header Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 shadow-xl">
        <div className="space-y-2 max-w-xl">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              Kịch bản hoàn tất · v{scriptData?.version || 1}
            </span>
            <span className="text-xs text-slate-400">⏱️ ~{session?.duration_minutes || 3} phút</span>
            <span className="text-xs text-slate-400">📝 {sentences.length} câu</span>
          </div>

          <h2 className="text-2xl font-heading font-bold text-white">
            {script.tieuDe || session?.topic || "Kịch bản bài giảng video"}
          </h2>
          <p className="text-xs text-slate-400 leading-relaxed">
            🎯 Mục tiêu: {session?.learning_goal}
          </p>
        </div>

        {/* Verification Summary Card & Export Actions */}
        <div className="flex flex-col sm:flex-row md:flex-col lg:flex-row items-stretch md:items-end gap-3 w-full md:w-auto">
          {/* Accuracy Score */}
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-center flex-1 sm:flex-initial">
            <div className="text-[11px] uppercase font-semibold tracking-wider text-slate-400">Trích dẫn xác thực</div>
            <div className="text-xl font-heading font-extrabold text-emerald-400 flex items-center justify-center gap-1">
              <span>{Math.round((verification?.accuracy_rate || 0) * 100)}%</span>
              <span className="text-xs text-slate-500 font-normal">({verification?.verified_count || 0}/{verification?.total_sentences_with_source || 0})</span>
            </div>
          </div>

          {/* Export Dropdown / Buttons */}
          <div className="flex items-center gap-2 flex-wrap">
            <button
              onClick={handleExportMarkdown}
              disabled={exporting}
              className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs shadow-md shadow-indigo-600/20 flex items-center gap-1.5 transition-all"
              title="Tải về file kịch bản markdown"
            >
              <span>📥 Xuất Markdown</span>
            </button>
            <button
              onClick={handleCopyMarkdown}
              className="px-3 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium text-xs border border-slate-700 flex items-center gap-1.5 transition-all"
              title="Sao chép văn bản kịch bản"
            >
              <span>📋 Copy</span>
            </button>
            <button
              onClick={handleExportJSON}
              disabled={exporting}
              className="px-3 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium text-xs border border-slate-700 flex items-center gap-1.5 transition-all"
              title="Xuất dữ liệu JSON kèm hồ sơ tài liệu"
            >
              <span>{ } JSON</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Split-View Container (2 Cột) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* ================= CỘT TRÁI: DANH SÁCH CÂU KỊCH BẢN (7 cột) ================= */}
        <div className="lg:col-span-7 space-y-4">
          {/* Filters Bar */}
          <div className="flex items-center justify-between gap-3 p-2 bg-slate-900 border border-slate-800 rounded-xl">
            <div className="flex items-center gap-1">
              <button
                onClick={() => setFilterType("all")}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                  filterType === "all" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
                }`}
              >
                Tất cả ({sentences.length})
              </button>
              <button
                onClick={() => setFilterType("cited")}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                  filterType === "cited" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
                }`}
              >
                Có trích dẫn ({sentences.filter(s => s.nguon && s.nguon.length > 0).length})
              </button>
              <button
                onClick={() => setFilterType("verified")}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                  filterType === "verified" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
                }`}
              >
                Đã đối soát ✓ ({verification?.verified_count || 0})
              </button>
            </div>

            <span className="text-[11px] text-slate-500 hidden sm:inline pr-2">
              💡 Bấm câu để xem bằng chứng gốc
            </span>
          </div>

          {/* Sentences List */}
          <div className="space-y-3">
            {filteredSentences.map((cau, idx) => {
              const isSelected = cau.n === selectedN;
              const hasSources = cau.nguon && cau.nguon.length > 0;
              const isVerified = cau.citation_verified === true;
              
              // Section title if first sentence of section
              const showSectionHeader = (idx === 0 || cau.phan !== filteredSentences[idx - 1]?.phan);

              return (
                <React.Fragment key={cau.n}>
                  {showSectionHeader && (
                    <div className="pt-4 pb-1">
                      <div className="flex items-center gap-2 text-xs font-heading font-bold uppercase tracking-wider text-indigo-400">
                        <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                        <span>Phần {cau.phan || 1}: {sectionMap[cau.phan] || `Nội dung phần ${cau.phan || 1}`}</span>
                      </div>
                    </div>
                  )}

                  <div
                    onClick={() => setSelectedN(cau.n)}
                    className={`p-4 rounded-2xl border transition-all cursor-pointer text-left relative ${
                      isSelected
                        ? "bg-indigo-950/30 border-indigo-500/80 shadow-lg shadow-indigo-950/50 ring-1 ring-indigo-500/40"
                        : "bg-slate-900 border-slate-800 hover:border-slate-700 hover:bg-slate-900/80"
                    }`}
                  >
                    {/* Sentence Top Meta */}
                    <div className="flex items-center justify-between gap-2 mb-2 text-xs">
                      <div className="flex items-center gap-2">
                        <span className={`font-mono text-xs font-bold px-2 py-0.5 rounded-md ${
                          isSelected ? "bg-indigo-600 text-white" : "bg-slate-800 text-slate-300"
                        }`}>
                          #{cau.n}
                        </span>

                        {cau.kieu && (
                          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[11px]">
                            {cau.kieu === 'giang' ? 'Giảng giải' : cau.kieu === 'nhe' ? 'Dẫn dắt' : cau.kieu === 'ke' ? 'Ví dụ/Kể' : cau.kieu}
                          </span>
                        )}
                      </div>

                      {/* Citation Badges */}
                      <div className="flex items-center gap-1.5">
                        {hasSources ? (
                          <>
                            {cau.nguon.map(code => (
                              <span key={code} className="font-mono text-[11px] font-semibold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                                {code}
                              </span>
                            ))}
                            <span className={`px-2 py-0.5 rounded text-[11px] font-medium flex items-center gap-1 ${
                              isVerified 
                                ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30" 
                                : "bg-amber-500/10 text-amber-400 border border-amber-500/30"
                            }`}>
                              {isVerified ? "✓ Verified" : "⚠️ Cần check"}
                            </span>
                          </>
                        ) : (
                          <span className="text-[11px] text-slate-500">Lời thoại chung</span>
                        )}
                      </div>
                    </div>

                    {/* Spoken sentence content */}
                    <p className="text-sm sm:text-base font-medium text-slate-100 leading-relaxed mb-2">
                      {cau.loi}
                    </p>

                    {/* Visual & On-screen direction */}
                    {(cau.trenManHinh || cau.yDoHinh) && (
                      <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-850 text-xs space-y-1">
                        {cau.trenManHinh && (
                          <div className="text-slate-400">
                            <span className="text-indigo-400 font-semibold">Màn hình:</span> {cau.trenManHinh}
                          </div>
                        )}
                        {cau.yDoHinh && (
                          <div className="text-slate-400">
                            <span className="text-emerald-400 font-semibold">Ý đồ hình:</span> {cau.yDoHinh}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* ================= CỘT PHẢI: BẰNG CHỨNG TRÍCH DẪN (5 cột, STICKY) ================= */}
        <div className="lg:col-span-5 lg:sticky lg:top-20 space-y-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
            {/* Header Inspector */}
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-indigo-500 animate-pulse"></span>
                <h3 className="font-heading font-bold text-base text-white">
                  Đối Chiếu Bằng Chứng Gốc
                </h3>
              </div>
              <span className="font-mono text-xs font-bold px-2.5 py-1 rounded-lg bg-indigo-600 text-white">
                Câu #{selectedSentence?.n || 1}
              </span>
            </div>

            {/* Selected Sentence Quote */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 space-y-1.5">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                Lời thoại đang chọn:
              </span>
              <p className="text-sm font-medium text-slate-200 leading-relaxed italic">
                "{selectedSentence?.loi}"
              </p>
            </div>

            {/* Citations & Evidence List */}
            {selectedSentence?.nguon && selectedSentence.nguon.length > 0 ? (
              <div className="space-y-4">
                <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between">
                  <span>Tài liệu nguồn ({selectedSentence.nguon.length})</span>
                  <span className="text-indigo-400">Đã qua Verify Agent</span>
                </div>

                {selectedSentence.nguon.map((code) => {
                  const source = sourceMap[code] || {};
                  const citationDetail = (selectedSentence.citation_details || []).find(c => c.code === code) || {};
                  const isVerified = citationDetail.verified !== false;
                  const overlap = citationDetail.overlap_ratio ? Math.round(citationDetail.overlap_ratio * 100) : null;

                  return (
                    <div key={code} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                      {/* Source header */}
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                            {code}
                          </span>
                          <span className="text-xs font-medium text-slate-300 line-clamp-1">
                            {source.title || source.url || `Nguồn ${code}`}
                          </span>
                        </div>
                        {source.url && (
                          <a
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-indigo-400 hover:text-indigo-300 whitespace-nowrap"
                          >
                            Mở link ↗
                          </a>
                        )}
                      </div>

                      {/* Verification Badge & Reason */}
                      <div className="flex items-center gap-2 text-xs">
                        <span className={`px-2 py-0.5 rounded font-semibold text-[11px] ${
                          isVerified ? "bg-emerald-500/20 text-emerald-400" : "bg-amber-500/20 text-amber-400"
                        }`}>
                          {isVerified ? "✓ Trùng khớp dữ liệu" : "⚠️ Cần kiểm tra lại"}
                        </span>
                        {overlap !== null && (
                          <span className="text-slate-400 text-[11px]">
                            Độ khớp từ khóa: <strong className="text-white">{overlap}%</strong>
                          </span>
                        )}
                      </div>

                      {/* Raw Excerpt Evidence */}
                      <div className="space-y-1">
                        <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                          Đoạn trích chứng minh từ web:
                        </span>
                        <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 font-mono leading-relaxed max-h-48 overflow-y-auto custom-scrollbar">
                          {citationDetail.excerpt || source.excerpt || "Không tìm thấy đoạn trích phù hợp."}
                        </div>
                      </div>

                      {citationDetail.reason && (
                        <p className="text-[11px] text-slate-400">
                          ℹ️ {citationDetail.reason}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="p-6 rounded-xl bg-slate-950/60 border border-slate-850 text-center space-y-2">
                <span className="text-2xl">💬</span>
                <p className="text-xs text-slate-400">
                  Câu này là lời dẫn dắt hoặc kết luận bài học, không chứa số liệu hay tuyên bố thực tế cần đối chiếu nguồn.
                </p>
              </div>
            )}
          </div>

          {/* Bottom Reset Action */}
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
            <button
              onClick={onBack}
              className="text-slate-400 hover:text-white transition-colors"
            >
              ← Quay lại chỉnh nguồn
            </button>
            <button
              onClick={onReset}
              className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors"
            >
              + Tạo bài giảng mới
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Render Root Component
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
