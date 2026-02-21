import { useState, useEffect, useRef } from 'react'
import { Play, Pause, RotateCcw, Code2, MessageSquare, Users } from 'lucide-react'
import { ChatScript as ChatScriptType, ScenarioItem, Character } from '../types'

interface ChatScriptProps {
  script: ChatScriptType
  className?: string
}

const CHARACTER_COLORS = [
  { badge: 'bg-blue-500/20 text-blue-300 border-blue-400/50', bubble: 'border-blue-500/30', dot: 'bg-blue-400' },
  { badge: 'bg-purple-500/20 text-purple-300 border-purple-400/50', bubble: 'border-purple-500/30', dot: 'bg-purple-400' },
  { badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-400/50', bubble: 'border-emerald-500/30', dot: 'bg-emerald-400' },
  { badge: 'bg-amber-500/20 text-amber-300 border-amber-400/50', bubble: 'border-amber-500/30', dot: 'bg-amber-400' },
  { badge: 'bg-rose-500/20 text-rose-300 border-rose-400/50', bubble: 'border-rose-500/30', dot: 'bg-rose-400' },
  { badge: 'bg-cyan-500/20 text-cyan-300 border-cyan-400/50', bubble: 'border-cyan-500/30', dot: 'bg-cyan-400' },
]

function getCharacterInitial(name: string): string {
  return name.charAt(0)
}

export default function ChatScript({ script, className = '' }: ChatScriptProps) {
  const [activeScenarioIndex, setActiveScenarioIndex] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentIndex, setCurrentIndex] = useState(-1)
  const [displayedDialogues, setDisplayedDialogues] = useState<number[]>([])
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const activeScenario: ScenarioItem | undefined = script.scenarios[activeScenarioIndex]

  const getCharacterColorIndex = (characterId: string): number => {
    if (!activeScenario) return 0
    const index = activeScenario.characters.findIndex(c => c.id === characterId)
    return index >= 0 ? index : 0
  }

  const getCharacterById = (characterId: string): Character | undefined => {
    return activeScenario?.characters.find(c => c.id === characterId)
  }

  const handleSelectScenario = (index: number) => {
    handleReset()
    setActiveScenarioIndex(index)
  }

  const handlePlay = () => {
    if (!activeScenario) return
    if (isPlaying) {
      handlePause()
    } else {
      setIsPlaying(true)
      if (currentIndex >= activeScenario.dialogues.length - 1) {
        setCurrentIndex(-1)
        setDisplayedDialogues([])
      }

      intervalRef.current = setInterval(() => {
        setCurrentIndex(prev => {
          const nextIndex = prev + 1
          if (!activeScenario || nextIndex >= activeScenario.dialogues.length) {
            handlePause()
            return prev
          }
          setDisplayedDialogues(prevDisplayed => [...prevDisplayed, nextIndex])
          return nextIndex
        })
      }, 2000)
    }
  }

  const handlePause = () => {
    setIsPlaying(false)
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }

  const handleReset = () => {
    handlePause()
    setCurrentIndex(-1)
    setDisplayedDialogues([])
  }

  const handleShowAll = () => {
    handlePause()
    if (!activeScenario) return
    const allIndices = activeScenario.dialogues.map((_, index) => index)
    setDisplayedDialogues(allIndices)
    setCurrentIndex(activeScenario.dialogues.length - 1)
  }

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [])

  if (!script.scenarios || script.scenarios.length === 0) {
    return (
      <div className={`chat-script ${className}`}>
        <div className="bg-white/5 border border-white/20 p-12 text-center">
          <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-40" />
          <p className="text-lg opacity-60">暂无群聊剧本数据</p>
          <p className="text-sm mt-2 opacity-40">AI 尚未生成操作链路的群聊剧本</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`chat-script ${className}`}>
      {/* 顶部说明 */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <MessageSquare className="w-5 h-5 opacity-60" />
          <h2 className="text-xl font-bold">服务之间怎么"说话"？</h2>
        </div>
        <p className="text-sm opacity-50">
          想象一下，这个项目里的各个模块就像一群同事，在一个微信群里聊天。当用户做某个操作时，各个模块就会在群里传话，互相配合完成任务。选一个场景，点播放按钮看看它们怎么聊天。
        </p>
      </div>

      {/* 场景选择卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {script.scenarios.map((scenario, index) => (
          <button
            key={scenario.id}
            onClick={() => handleSelectScenario(index)}
            className={`text-left p-5 border transition-all duration-200 cursor-pointer ${
              activeScenarioIndex === index
                ? 'bg-white/10 border-white/40'
                : 'bg-white/5 border-white/15 hover:bg-white/8 hover:border-white/25'
            }`}
          >
            <div className="flex items-start justify-between mb-2">
              <h3 className="font-semibold text-white">{scenario.title}</h3>
              {index === 0 && (
                <span className="text-xs px-2 py-0.5 bg-white/20 text-white/80 rounded-full whitespace-nowrap ml-2">
                  核心功能
                </span>
              )}
            </div>
            <p className="text-sm text-white/50 line-clamp-2">{scenario.description}</p>
          </button>
        ))}
      </div>

      {/* 选中场景的详情 */}
      {activeScenario && (
        <div className="border border-white/20 bg-white/5">
          {/* 场景头部 */}
          <div className="flex items-center justify-between p-5 border-b border-white/10">
            <div className="flex items-center gap-3">
              <MessageSquare className="w-5 h-5 opacity-60" />
              <div>
                <h3 className="font-semibold text-lg">{activeScenario.title}</h3>
                <p className="text-sm opacity-50">{activeScenario.description}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handlePlay}
                disabled={currentIndex >= activeScenario.dialogues.length - 1 && displayedDialogues.length > 0}
                className="w-10 h-10 flex items-center justify-center bg-white/10 hover:bg-white/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              >
                {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              </button>
              <button
                onClick={handleReset}
                className="w-10 h-10 flex items-center justify-center bg-white/10 hover:bg-white/20 transition-colors"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
              <button
                onClick={handleShowAll}
                className="w-10 h-10 flex items-center justify-center bg-white/10 hover:bg-white/20 transition-colors"
                title="显示全部对话"
              >
                <Users className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* 参与角色 */}
          <div className="px-5 py-4 border-b border-white/10">
            <div className="flex items-center gap-2 mb-3">
              <Users className="w-4 h-4 opacity-40" />
              <span className="text-sm opacity-50">参与角色（{activeScenario.characters.length} 位）</span>
            </div>
            <div className="flex flex-wrap gap-3">
              {activeScenario.characters.map((character, charIndex) => {
                const colorStyle = CHARACTER_COLORS[charIndex % CHARACTER_COLORS.length]
                return (
                  <div
                    key={character.id}
                    className={`flex items-center gap-2 px-3 py-1.5 border rounded-full ${colorStyle.badge}`}
                  >
                    <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold ${colorStyle.dot} text-black`}>
                      {getCharacterInitial(character.name)}
                    </span>
                    <span className="text-sm font-medium">{character.name}</span>
                  </div>
                )
              })}
            </div>
          </div>

          {/* 对话消息流 */}
          <div className="p-5 space-y-5 max-h-[600px] overflow-y-auto">
            {activeScenario.dialogues.map((dialogue, index) => {
              const fromCharacter = getCharacterById(dialogue.from)
              const toCharacter = getCharacterById(dialogue.to)
              const colorIndex = getCharacterColorIndex(dialogue.from)
              const colorStyle = CHARACTER_COLORS[colorIndex % CHARACTER_COLORS.length]
              const isDisplayed = displayedDialogues.includes(index)
              const isCurrent = index === currentIndex

              return (
                <div
                  key={index}
                  className={`transition-all duration-500 ${
                    isDisplayed ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4 pointer-events-none h-0 overflow-hidden'
                  }`}
                >
                  {/* 发送方 → 接收方 */}
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${colorStyle.dot} text-black`}>
                      {fromCharacter ? getCharacterInitial(fromCharacter.name) : '?'}
                    </span>
                    <span className="font-semibold text-sm" style={{ color: colorStyle.dot.replace('bg-', '').includes('blue') ? '#93c5fd' : undefined }}>
                      {fromCharacter?.name || dialogue.from}
                    </span>
                    <span className="text-white/30 text-xs">→</span>
                    <span className="text-sm text-white/60">
                      {toCharacter?.name || dialogue.to}
                    </span>
                    {isCurrent && (
                      <span className="ml-auto flex items-center gap-1 text-xs opacity-60">
                        <div className="w-1.5 h-1.5 bg-white rounded-full animate-pulse" />
                        正在发送...
                      </span>
                    )}
                  </div>

                  {/* 消息气泡 */}
                  <div className={`ml-8 border-l-2 ${colorStyle.bubble} pl-4 py-2`}>
                    <p className="text-white/90 leading-relaxed">{dialogue.content}</p>
                    {dialogue.codeRef && (
                      <div className="flex items-center gap-2 mt-2 text-xs opacity-50">
                        <Code2 className="w-3 h-3" />
                        <code className="bg-black/30 px-1.5 py-0.5 rounded">{dialogue.codeRef}</code>
                      </div>
                    )}
                  </div>
                </div>
              )
            })}

            {/* 空状态提示 */}
            {displayedDialogues.length === 0 && (
              <div className="text-center py-12 opacity-40">
                <Play className="w-8 h-8 mx-auto mb-3" />
                <p>点击播放按钮，看看模块们怎么聊天</p>
              </div>
            )}
          </div>

          {/* 进度条 */}
          {activeScenario.dialogues.length > 0 && displayedDialogues.length > 0 && (
            <div className="px-5 pb-4">
              <div className="flex items-center justify-between text-xs opacity-40 mb-1">
                <span>{displayedDialogues.length} / {activeScenario.dialogues.length} 条消息</span>
              </div>
              <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
                <div
                  className="h-full bg-white/60 transition-all duration-500 rounded-full"
                  style={{ width: `${(displayedDialogues.length / activeScenario.dialogues.length) * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
