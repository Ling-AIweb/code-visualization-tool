import { useState } from 'react'
import { Search, BookOpen, Lightbulb, ChevronDown, FileCode2 } from 'lucide-react'
import { TermExplanation } from '../types'

interface TermDictionaryProps {
  terms: TermExplanation[]
  className?: string
}

export default function TermDictionary({ terms, className = '' }: TermDictionaryProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedTermId, setExpandedTermId] = useState<string | null>(null)

  const filteredTerms = terms.filter(term =>
    term.term.toLowerCase().includes(searchQuery.toLowerCase()) ||
    term.laymanExplanation.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const toggleExpand = (termName: string) => {
    setExpandedTermId(prev => prev === termName ? null : termName)
  }

  return (
    <div className={`term-dictionary ${className}`}>
      {/* 标题 */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-3">术语词典</h2>
        <p className="text-lg opacity-60">用大白话解释技术名词</p>
      </div>

      {/* 搜索框 */}
      <div className="mb-8 relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 opacity-40" />
        <input
          type="text"
          placeholder="搜索术语或解释..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="input-field pl-12 pr-4 py-4 text-lg"
        />
      </div>

      {/* 术语列表 */}
      <div className="grid gap-3">
        {filteredTerms.length > 0 ? (
          filteredTerms.map((term, index) => {
            const isExpanded = expandedTermId === term.term
            return (
              <div
                key={index}
                className="card border-thin overflow-hidden transition-all duration-300"
              >
                {/* 折叠头部 - 点击展开/收起 */}
                <div
                  onClick={() => toggleExpand(term.term)}
                  className="p-5 cursor-pointer transition-colors duration-200 hover:bg-black/[0.03]"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-1.5 flex-wrap">
                        <BookOpen className="w-5 h-5 flex-shrink-0 opacity-70" />
                        <h3 className="text-xl font-bold">{term.term}</h3>
                        {/* 关联组件标签 */}
                        {term.relatedComponent && (
                          <span className="text-xs px-2.5 py-0.5 bg-white/10 border border-white/20 opacity-60">
                            {term.relatedComponent}
                          </span>
                        )}
                        {/* 关联文件标签 */}
                        {term.relatedFiles && term.relatedFiles.length > 0 && (
                          term.relatedFiles.map((filePath, fileIndex) => (
                            <span
                              key={fileIndex}
                              className="text-xs px-2.5 py-0.5 bg-purple-500/15 border border-purple-400/30 text-purple-300 font-mono"
                            >
                              {filePath}
                            </span>
                          ))
                        )}
                      </div>
                      <p className="opacity-60 leading-relaxed text-sm pl-8">
                        {term.laymanExplanation}
                      </p>
                    </div>
                    <ChevronDown
                      className={`w-5 h-5 flex-shrink-0 ml-4 opacity-40 transition-transform duration-300 ${
                        isExpanded ? 'rotate-180' : ''
                      }`}
                    />
                  </div>
                </div>

                {/* 展开详情区域 */}
                <div
                  className={`transition-all duration-300 ease-in-out ${
                    isExpanded
                      ? 'max-h-[600px] opacity-100'
                      : 'max-h-0 opacity-0'
                  } overflow-hidden`}
                >
                  <div className="px-5 pb-5 border-t border-white/10">
                    {/* 生活化类比 */}
                    {term.analogy && (
                      <div className="mt-4 p-4 bg-yellow-500/5 border border-yellow-500/20">
                        <div className="flex items-center gap-2 mb-2">
                          <Lightbulb className="w-4 h-4 text-yellow-400" />
                          <span className="text-sm font-semibold text-yellow-400">打个比方</span>
                        </div>
                        <p className="text-sm leading-relaxed opacity-80 pl-6">
                          {term.analogy}
                        </p>
                      </div>
                    )}

                    {/* 技术解释 */}
                    {term.technicalExplanation && (
                      <div className="mt-3 p-4 bg-white/5 border border-white/10">
                        <h4 className="text-sm font-semibold mb-2 opacity-70">技术解释</h4>
                        <p className="text-sm leading-relaxed opacity-60">
                          {term.technicalExplanation}
                        </p>
                      </div>
                    )}

                    {/* 关联代码文件 */}
                    {term.relatedFiles && term.relatedFiles.length > 0 && (
                      <div className="mt-3 p-4 bg-white/5 border border-white/10">
                        <div className="flex items-center gap-2 mb-2">
                          <FileCode2 className="w-4 h-4 opacity-70" />
                          <h4 className="text-sm font-semibold opacity-70">关联代码文件</h4>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {term.relatedFiles.map((filePath, fileIndex) => (
                            <span
                              key={fileIndex}
                              className="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 bg-purple-500/10 border border-purple-400/25 text-purple-300 font-mono hover:bg-purple-500/20 transition-colors"
                            >
                              <FileCode2 className="w-3 h-3" />
                              {filePath}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 实际应用示例 */}
                    {term.examples && term.examples.length > 0 && (
                      <div className="mt-3">
                        <h4 className="text-sm font-semibold mb-2 opacity-70">实际应用</h4>
                        <div className="space-y-2">
                          {term.examples.map((example, exIndex) => (
                            <div
                              key={exIndex}
                              className="p-3 bg-white/5 border border-white/10 text-sm"
                            >
                              <p className="opacity-70">{example}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )
          })
        ) : (
          <div className="text-center py-12 opacity-40">
            <BookOpen className="w-12 h-12 mx-auto mb-4" />
            <p className="text-lg">没有找到相关术语</p>
          </div>
        )}
      </div>
    </div>
  )
}
