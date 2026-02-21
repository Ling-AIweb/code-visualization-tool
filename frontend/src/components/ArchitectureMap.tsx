import { useState } from 'react'
import { ArchitectureGraph, ArchitectureLayer } from '../types'
import { Layers, ChevronDown, ChevronUp, FileCode2 } from 'lucide-react'

interface ArchitectureMapProps {
  graph: ArchitectureGraph
  className?: string
}

const LAYER_STYLES = [
  { gradient: 'from-blue-500/20 to-blue-600/10', border: 'border-blue-500/40', badge: 'bg-blue-500/20 text-blue-300', dot: 'bg-blue-400' },
  { gradient: 'from-emerald-500/20 to-emerald-600/10', border: 'border-emerald-500/40', badge: 'bg-emerald-500/20 text-emerald-300', dot: 'bg-emerald-400' },
  { gradient: 'from-amber-500/20 to-amber-600/10', border: 'border-amber-500/40', badge: 'bg-amber-500/20 text-amber-300', dot: 'bg-amber-400' },
  { gradient: 'from-purple-500/20 to-purple-600/10', border: 'border-purple-500/40', badge: 'bg-purple-500/20 text-purple-300', dot: 'bg-purple-400' },
  { gradient: 'from-rose-500/20 to-rose-600/10', border: 'border-rose-500/40', badge: 'bg-rose-500/20 text-rose-300', dot: 'bg-rose-400' },
]

function LayerCard({ layer, index }: { layer: ArchitectureLayer; index: number }) {
  const [expanded, setExpanded] = useState(index === 0)
  const style = LAYER_STYLES[index % LAYER_STYLES.length]

  return (
    <div className={`relative border ${style.border} bg-gradient-to-r ${style.gradient} transition-all duration-300`}>
      {/* 层级连接线 */}
      {index > 0 && (
        <div className="absolute -top-6 left-1/2 -translate-x-1/2 flex flex-col items-center">
          <div className="w-px h-4 bg-white/20" />
          <div className="text-white/30 text-xs">▼</div>
        </div>
      )}

      {/* 层级头部 */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-5 cursor-pointer hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${style.dot}`} />
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-semibold text-white">{layer.name}</h3>
              <span className={`text-xs px-2 py-0.5 rounded-full ${style.badge}`}>
                {layer.components?.length || 0} 个组件
              </span>
            </div>
            <p className="text-sm text-white/60 mt-1 text-left">{layer.plainExplanation || layer.description}</p>
          </div>
        </div>
        {expanded ? <ChevronUp className="w-5 h-5 text-white/40" /> : <ChevronDown className="w-5 h-5 text-white/40" />}
      </button>

      {/* 组件列表 */}
      {expanded && layer.components && layer.components.length > 0 && (
        <div className="px-5 pb-5 grid grid-cols-1 md:grid-cols-2 gap-3">
          {layer.components.map((component, componentIndex) => (
            <div
              key={componentIndex}
              className="bg-black/30 border border-white/10 p-4 hover:border-white/30 transition-all duration-200"
            >
              <div className="flex items-center gap-2 mb-2">
                <span className="font-medium text-white">{component.name}</span>
                {component.role && (
                  <span className="text-xs px-1.5 py-0.5 bg-white/10 text-white/50 rounded">
                    {component.role}
                  </span>
                )}
              </div>
              <p className="text-sm text-white/50 leading-relaxed mb-3">
                {component.plainExplanation || component.description}
              </p>
              {/* 文件列表 */}
              {component.files && component.files.length > 0 && (
                <div className="mt-3 pt-3 border-t border-white/10">
                  <div className="flex items-center gap-1.5 mb-2 text-xs text-white/40">
                    <FileCode2 className="w-3 h-3" />
                    <span>相关文件</span>
                  </div>
                  <div className="space-y-1">
                    {component.files.map((file, fileIndex) => (
                      <div
                        key={fileIndex}
                        className="text-xs text-white/50 font-mono bg-black/30 px-2 py-1 rounded truncate hover:text-white/70 transition-colors"
                        title={file}
                      >
                        {file}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function ArchitectureMap({ graph, className = '' }: ArchitectureMapProps) {
  const hasLayers = graph.layers && graph.layers.length > 0

  if (!hasLayers) {
    return (
      <div className={`architecture-map ${className}`}>
        <div className="bg-white/5 border border-white/20 p-12">
          <div className="text-center opacity-60">
            <Layers className="w-12 h-12 mx-auto mb-4 opacity-40" />
            <p className="text-lg">暂无架构数据</p>
            <p className="text-sm mt-2">AI 尚未生成架构分析结果</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`architecture-map ${className}`}>
      {graph.description && (
        <div className="mb-6">
          <p className="text-lg opacity-80 leading-relaxed">{graph.description}</p>
        </div>
      )}

      {/* 分层架构展示 */}
      <div className="space-y-6">
        {graph.layers!.map((layer, index) => (
          <LayerCard key={layer.id || index} layer={layer} index={index} />
        ))}
      </div>

      {/* 图例说明 */}
      <div className="mt-8 flex flex-wrap gap-4 text-sm opacity-50">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-blue-400" />
          <span>展示层</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-emerald-400" />
          <span>逻辑层</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-amber-400" />
          <span>数据层</span>
        </div>
      </div>
    </div>
  )
}
