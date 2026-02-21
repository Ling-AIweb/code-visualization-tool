import { useState } from 'react'
import { Search, BookOpen, Lightbulb, ChevronRight, X } from 'lucide-react'
import { TermExplanation } from '../types'

interface TermDictionaryProps {
  terms: TermExplanation[]
  className?: string
}

export default function TermDictionary({ terms, className = '' }: TermDictionaryProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedTerm, setSelectedTerm] = useState<TermExplanation | null>(null)

  const filteredTerms = terms.filter(term =>
    term.term.toLowerCase().includes(searchQuery.toLowerCase()) ||
    term.laymanExplanation.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleTermClick = (term: TermExplanation) => {
    setSelectedTerm(term)
  }

  const handleCloseDetail = () => {
    setSelectedTerm(null)
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
      <div className="grid gap-4">
        {filteredTerms.length > 0 ? (
          filteredTerms.map((term, index) => (
            <div
              key={index}
              onClick={() => handleTermClick(term)}
              className={`card border-thin p-6 cursor-pointer transition-all duration-300 hover:border-white hover:bg-white hover:text-black ${
                selectedTerm?.term === term.term ? 'bg-white text-black border-white' : ''
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <BookOpen className="w-5 h-5 flex-shrink-0" />
                    <h3 className="text-xl font-bold">{term.term}</h3>
                  </div>
                  <p className="opacity-70 leading-relaxed line-clamp-2">
                    {term.laymanExplanation}
                  </p>
                </div>
                <ChevronRight className="w-5 h-5 flex-shrink-0 mt-1" />
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-12 opacity-40">
            <BookOpen className="w-12 h-12 mx-auto mb-4" />
            <p className="text-lg">没有找到相关术语</p>
          </div>
        )}
      </div>

      {/* 详细解释弹窗 */}
      {selectedTerm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="absolute inset-0 bg-black/80 backdrop-blur-sm"
            onClick={handleCloseDetail}
          />
          <div className="relative bg-black border border-white/30 p-8 max-w-2xl w-full max-h-[80vh] overflow-y-auto animate-fade-in">
            {/* 关闭按钮 */}
            <button
              onClick={handleCloseDetail}
              className="absolute top-4 right-4 w-10 h-10 flex items-center justify-center hover:bg-white/10 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>

            {/* 术语标题 */}
            <div className="mb-6">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-12 h-12 bg-white text-black rounded-full flex items-center justify-center">
                  <BookOpen className="w-6 h-6" />
                </div>
                <h3 className="text-4xl font-bold">{selectedTerm.term}</h3>
              </div>
            </div>

            {/* 生活化解释 */}
            <div className="mb-8 p-6 bg-white/5 border border-white/20">
              <div className="flex items-center gap-2 mb-3">
                <Lightbulb className="w-5 h-5 text-yellow-400" />
                <h4 className="text-lg font-semibold">大白话解释</h4>
              </div>
              <p className="text-lg leading-relaxed">
                {selectedTerm.laymanExplanation}
              </p>
            </div>

            {/* 技术解释 */}
            <div className="mb-8 p-6 bg-white/5 border border-white/20">
              <h4 className="text-lg font-semibold mb-3">技术解释</h4>
              <p className="text-lg leading-relaxed opacity-80">
                {selectedTerm.technicalExplanation}
              </p>
            </div>

            {/* 实例 */}
            {selectedTerm.examples && selectedTerm.examples.length > 0 && (
              <div>
                <h4 className="text-lg font-semibold mb-3">实际应用</h4>
                <div className="space-y-3">
                  {selectedTerm.examples.map((example, index) => (
                    <div
                      key={index}
                      className="p-4 bg-white/5 border border-white/10 rounded-none"
                    >
                      <p className="opacity-80">{example}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
