import { ExternalLink } from 'lucide-react';

const TweetCard = ({ tweet }) => {
    // Handle schema change: DB uses user_info, mock used user
    const user = tweet.user_info || tweet.user || { username: 'unknown' };
    const { id, text, risk_analysis, collected_at, url } = tweet;
    const riskScore = risk_analysis?.risk_score || 0;

    // Determine color based on risk score
    const getRiskColor = (score) => {
        if (score >= 7) return 'bg-red-500/10 border-red-500/50 text-red-400';
        if (score >= 4) return 'bg-orange-500/10 border-orange-500/50 text-orange-400';
        return 'bg-green-500/10 border-green-500/50 text-green-400';
    };

    const riskColorClass = getRiskColor(riskScore);
    const initial = user.username ? user.username[0].toUpperCase() : '?';
    const tweetUrl = url || `https://twitter.com/${user.username}/status/${id}`;

    return (
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 border border-slate-700 hover:border-slate-600 transition-all duration-300 shadow-lg relative group">
            <a
                href={tweetUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="absolute top-4 right-4 text-slate-500 hover:text-blue-400 transition-colors"
                title="View on X (Twitter)"
            >
                <ExternalLink size={18} />
            </a>

            <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center font-bold text-white">
                        {initial}
                    </div>
                    <div className="text-left">
                        <h3 className="font-semibold text-slate-200">@{user.username || 'unknown'}</h3>
                        <p className="text-xs text-slate-400">{new Date(collected_at).toLocaleString()}</p>
                    </div>
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-medium border ${riskColorClass} mr-8`}>
                    リスク: {riskScore}/10
                </div>
            </div>

            <p className="text-slate-300 text-left mb-4 text-sm leading-relaxed whitespace-pre-wrap">
                {text}
            </p>

            {risk_analysis && (
                <div className="bg-slate-900/50 rounded-lg p-3 text-xs text-left text-slate-400 border border-slate-700/50">
                    <div className="flex justify-between mb-2">
                        <span className="flex flex-col">
                            <span className="text-[10px] uppercase tracking-wider opacity-70">攻撃性</span>
                            <span className="font-semibold text-orange-300">{risk_analysis.aggression}/10</span>
                        </span>
                        <span className="flex flex-col text-right">
                            <span className="text-[10px] uppercase tracking-wider opacity-70">拡散リスク</span>
                            <span className="font-semibold text-purple-300">{risk_analysis.spread_risk}/10</span>
                        </span>
                    </div>
                    <div className="border-t border-slate-800 pt-2 mt-1">
                        <span className="text-[10px] uppercase tracking-wider opacity-70 block mb-1">AI判定理由:</span>
                        <p className="italic opacity-90 leading-relaxed text-slate-300">
                            {risk_analysis.reason}
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TweetCard;
