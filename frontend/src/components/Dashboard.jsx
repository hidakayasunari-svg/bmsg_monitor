import React, { useState, useEffect } from 'react';
import TweetCard from './TweetCard';
import { supabase } from '../lib/supabaseClient';
import { HelpCircle, Info, Activity, Play, RefreshCw } from 'lucide-react';

// Sub-component for System Status
const SystemStatusWidget = () => {
    const [status, setStatus] = useState('Idle');
    const [lastLog, setLastLog] = useState('');
    const [isRequesting, setIsRequesting] = useState(false);

    useEffect(() => {
        const fetchStatus = async () => {
            const { data } = await supabase
                .from('system_logs')
                .select('*')
                .order('created_at', { ascending: false })
                .limit(1);
            if (data && data[0]) {
                setLastLog(data[0].message);
                // Simple heuristic: if log is recent and contains "STARTED" or "Searching", consider active
                setStatus('Active');
            }
        };
        fetchStatus();
        const interval = setInterval(fetchStatus, 3000); // Poll every 3s
        return () => clearInterval(interval);
    }, []);

    const handleRunNow = async () => {
        setIsRequesting(true);
        try {
            await supabase.from('system_commands').insert([{ command: 'RUN_NOW' }]);
            setLastLog("Run command requested...");
        } catch (e) {
            console.error(e);
        } finally {
            setTimeout(() => setIsRequesting(false), 2000);
        }
    };

    return (
        <div className="bg-slate-800/80 border border-slate-700 rounded-lg p-3 flex items-center gap-4 text-sm min-w-[300px]">
            <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                    <Activity size={14} className="text-blue-400" />
                    <span className="font-bold text-slate-300">System Status</span>
                </div>
                <p className="text-xs text-slate-400 truncate max-w-[200px]" title={lastLog}>
                    {lastLog || 'Initializing...'}
                </p>
            </div>

            <button
                onClick={handleRunNow}
                disabled={isRequesting}
                className={`flex items-center gap-2 px-3 py-2 rounded-md font-bold transition-all ${isRequesting
                    ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-900/20'
                    }`}
            >
                {isRequesting ? <RefreshCw size={16} className="animate-spin" /> : <Play size={16} fill="currentColor" />}
                {isRequesting ? 'Sent' : 'Run Now'}
            </button>
        </div>
    );
};


const Dashboard = () => {
    const [tweets, setTweets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isHelpOpen, setIsHelpOpen] = useState(false);

    // Filtering States
    const [minRisk, setMinRisk] = useState(0);
    const [sortOrder, setSortOrder] = useState('date'); // 'date' or 'risk'
    const [dateRange, setDateRange] = useState({ start: '', end: '' });

    useEffect(() => {
        fetchTweets();
    }, [minRisk, sortOrder, dateRange]); // Re-fetch when filters change

    const fetchTweets = async () => {
        try {
            setLoading(true);
            let query = supabase
                .from('tweets')
                .select('*');

            // Apply Risk Filter
            if (minRisk > 0) {
                query = query.gte('risk_score', minRisk);
            }

            // Apply Date Filter
            if (dateRange.start) {
                query = query.gte('collected_at', new Date(dateRange.start).toISOString());
            }
            if (dateRange.end) {
                // Add 1 day to include the end date fully
                const endDate = new Date(dateRange.end);
                endDate.setDate(endDate.getDate() + 1);
                query = query.lt('collected_at', endDate.toISOString());
            }

            // Apply Sorting
            if (sortOrder === 'risk') {
                query = query.order('risk_score', { ascending: false });
            } else {
                query = query.order('collected_at', { ascending: false });
            }

            const { data, error } = await query.limit(50);

            if (error) throw error;
            setTweets(data || []);
        } catch (err) {
            console.error('Error fetching tweets:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const highRiskCount = tweets.filter(t => (t.risk_score || t.risk_analysis?.risk_score) >= 7).length;



    // Render loading/error states INSIDE the main layout, not as early returns
    const renderContent = () => {
        if (loading && tweets.length === 0) {
            return (
                <div className="text-center py-20">
                    <p className="text-slate-400 animate-pulse">Loading monitor data...</p>
                </div>
            );
        }

        if (error) {
            return (
                <div className="text-center py-20 text-red-400">
                    Error loading data: {error}
                </div>
            );
        }

        if (tweets.length === 0) {
            return (
                <div className="text-center py-20 bg-slate-800/30 rounded-xl border border-dashed border-slate-700">
                    <p className="text-slate-400">データベースにツイートが見つかりません。</p>
                    <p className="text-sm text-slate-500 mt-2">条件を変更するか、バックエンドを実行してください。</p>
                </div>
            );
        }

        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {tweets.map(tweet => (
                    <TweetCard key={tweet.id} tweet={tweet} />
                ))}
            </div>
        );
    };

    return (
        <div className="w-full max-w-6xl mx-auto p-6 relative">
            <header className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                <div>
                    <div className="flex items-center gap-3">
                        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
                            BMSG Monitor
                        </h1>
                        <button
                            onClick={() => setIsHelpOpen(!isHelpOpen)}
                            className="text-slate-500 hover:text-blue-400 transition-colors"
                            title="リスクスコアについて"
                        >
                            <HelpCircle size={24} />
                        </button>
                    </div>
                    <p className="text-slate-400 text-sm mt-1">リアルタイム・リスク分析ダッシュボード</p>

                    {isHelpOpen && (
                        <div className="absolute top-20 left-0 z-50 bg-slate-800 border border-slate-700 p-6 rounded-xl shadow-2xl w-full max-w-md text-left">
                            <div className="flex justify-between items-center mb-4 border-b border-slate-700 pb-2">
                                <h3 className="font-bold text-white flex items-center gap-2">
                                    <Info size={18} className="text-blue-400" />
                                    リスクスコアの解説
                                </h3>
                                <button onClick={() => setIsHelpOpen(false)} className="text-slate-400 hover:text-white">✕</button>
                            </div>
                            <ul className="space-y-3 text-sm text-slate-300">
                                <li>
                                    <span className="font-bold text-blue-200 block">感情スコア (Sentiment)</span>
                                    投稿の「ネガティブ度」を判定します。-1.0 に近いほど否定的な感情を含みます。
                                </li>
                                <li>
                                    <span className="font-bold text-orange-200 block">攻撃性 (Aggression)</span>
                                    敵意、侮辱、暴言の強さを 0~10 で評価します。
                                </li>
                                <li>
                                    <span className="font-bold text-purple-200 block">拡散リスク (Spread Risk)</span>
                                    炎上や議論呼ぶ可能性（拡散されやすさ）を予測します。
                                </li>
                                <li>
                                    <span className="font-bold text-red-200 block">総合リスク (Risk Score)</span>
                                    上記を統合した危険度です。7点以上は「高リスク（要警戒）」と判定されます。
                                </li>
                            </ul>
                        </div>
                    )}
                </div>

                {/* System Status & Controls */}
                <div className="flex flex-col gap-2 w-full md:w-auto mt-4 md:mt-0">
                    <SystemStatusWidget />
                </div>

                {/* Stats */}
                <div className="flex gap-4 self-end md:self-auto">
                    <div className="bg-slate-800 rounded-lg p-3 text-center min-w-[100px] border border-slate-700">
                        <p className="text-2xl font-bold text-white">{tweets.length}</p>
                        <p className="text-xs text-slate-500 uppercase tracking-wider">表示件数</p>
                    </div>
                    <div className="bg-slate-800 rounded-lg p-3 text-center min-w-[100px] border border-red-900/30">
                        <p className="text-2xl font-bold text-red-400">
                            {highRiskCount}
                        </p>
                        <p className="text-xs text-red-500/70 uppercase tracking-wider">高リスク</p>
                    </div>
                </div>
            </header>

            {/* Filters Bar */}
            <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700 mb-6 flex flex-wrap gap-4 items-center shadow-sm">

                {/* Risk Filter */}
                <div className="flex items-center gap-2">
                    <label className="text-sm text-slate-400 font-medium">リスク:</label>
                    <select
                        value={minRisk}
                        onChange={(e) => setMinRisk(Number(e.target.value))}
                        className="bg-slate-900 border border-slate-600 text-slate-200 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2"
                    >
                        <option value={0}>すべて (All)</option>
                        <option value={4}>中リスク以上 (4+)</option>
                        <option value={7}>高リスクのみ (7+)</option>
                    </select>
                </div>

                {/* Sort Order */}
                <div className="flex items-center gap-2">
                    <label className="text-sm text-slate-400 font-medium">並び替え:</label>
                    <div className="flex bg-slate-900 rounded-lg p-1 border border-slate-600">
                        <button
                            onClick={() => setSortOrder('date')}
                            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${sortOrder === 'date' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
                        >
                            新しい順
                        </button>
                        <button
                            onClick={() => setSortOrder('risk')}
                            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${sortOrder === 'risk' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
                        >
                            危険度順
                        </button>
                    </div>
                </div>

                {/* Date Range */}
                <div className="flex items-center gap-2 ml-auto">
                    <input
                        type="date"
                        value={dateRange.start}
                        onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
                        className="bg-slate-900 border border-slate-600 text-slate-200 text-sm rounded-lg p-2 w-32 md:w-auto"
                        placeholder="Start Date"
                    />
                    <span className="text-slate-500">~</span>
                    <input
                        type="date"
                        value={dateRange.end}
                        onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
                        className="bg-slate-900 border border-slate-600 text-slate-200 text-sm rounded-lg p-2 w-32 md:w-auto"
                        placeholder="End Date"
                    />
                </div>
            </div>

            {loading && (
                <div className="absolute inset-0 bg-slate-900/50 backdrop-blur-[1px] flex items-center justify-center z-10 rounded-xl">
                    <div className="animate-pulse text-blue-400">Loading...</div>
                </div>
            )}


            {renderContent()}
        </div>
    );
};

export default Dashboard;
