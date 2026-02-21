import { useState } from 'react'
import { ChevronRight, ChevronDown, Folder, File, FileCode, FileText, Image, Archive } from 'lucide-react'
import { ProjectStructure as ProjectStructureType } from '../types'

interface ProjectStructureTreeProps {
  structure: ProjectStructureType
  onNodeClick?: (node: ProjectStructureType) => void
  className?: string
}

export default function ProjectStructureTree({ structure, onNodeClick, className = '' }: ProjectStructureTreeProps) {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set())

  const toggleNode = (path: string) => {
    setExpandedNodes((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(path)) {
        newSet.delete(path)
      } else {
        newSet.add(path)
      }
      return newSet
    })
  }

  const getFileIcon = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase()
    const iconMap: Record<string, React.ReactNode> = {
      'js': <FileCode className="w-4 h-4" />,
      'jsx': <FileCode className="w-4 h-4" />,
      'ts': <FileCode className="w-4 h-4" />,
      'tsx': <FileCode className="w-4 h-4" />,
      'py': <FileCode className="w-4 h-4" />,
      'java': <FileCode className="w-4 h-4" />,
      'go': <FileCode className="w-4 h-4" />,
      'rs': <FileCode className="w-4 h-4" />,
      'html': <FileText className="w-4 h-4" />,
      'css': <FileText className="w-4 h-4" />,
      'scss': <FileText className="w-4 h-4" />,
      'json': <FileText className="w-4 h-4" />,
      'md': <FileText className="w-4 h-4" />,
      'txt': <FileText className="w-4 h-4" />,
      'png': <Image className="w-4 h-4" />,
      'jpg': <Image className="w-4 h-4" />,
      'jpeg': <Image className="w-4 h-4" />,
      'gif': <Image className="w-4 h-4" />,
      'svg': <Image className="w-4 h-4" />,
      'zip': <Archive className="w-4 h-4" />,
      'tar': <Archive className="w-4 h-4" />,
      'gz': <Archive className="w-4 h-4" />,
    }
    return iconMap[ext || ''] || <File className="w-4 h-4" />
  }

  const renderNode = (node: ProjectStructureType, level: number = 0) => {
    const isExpanded = expandedNodes.has(node.path)
    const isFolder = node.type === 'folder'
    const hasChildren = isFolder && node.children && node.children.length > 0

    return (
      <div key={node.path} className="select-none">
        {/* 节点行 */}
        <div
          onClick={() => {
            if (hasChildren) {
              toggleNode(node.path)
            }
            if (onNodeClick) {
              onNodeClick(node)
            }
          }}
          className={`
            flex items-center gap-2 py-2 px-3 cursor-pointer
            transition-all duration-200 rounded-none
            hover:bg-white/10 group
          `}
          style={{ paddingLeft: `${level * 16 + 12}px` }}
        >
          {/* 展开/折叠图标 */}
          <div className="w-5 h-5 flex items-center justify-center flex-shrink-0">
            {hasChildren ? (
              isExpanded ? (
                <ChevronDown className="w-4 h-4 opacity-60" />
              ) : (
                <ChevronRight className="w-4 h-4 opacity-60" />
              )
            ) : null}
          </div>

          {/* 文件/文件夹图标 */}
          <div className="w-5 h-5 flex items-center justify-center flex-shrink-0">
            {isFolder ? (
              <Folder className="w-4 h-4 opacity-80 group-hover:opacity-100 transition-opacity" />
            ) : (
              <span className="opacity-80 group-hover:opacity-100 transition-opacity">
                {getFileIcon(node.name)}
              </span>
            )}
          </div>

          {/* 文件名 */}
          <span className={`
            text-sm truncate transition-colors
            ${isFolder ? 'font-semibold' : 'opacity-80'}
            group-hover:opacity-100
          `}>
            {node.name}
          </span>

          {/* 描述（如果有） */}
          {node.description && (
            <span className="text-xs opacity-40 ml-auto truncate max-w-[200px]">
              {node.description}
            </span>
          )}
        </div>

        {/* 子节点 */}
        {isExpanded && hasChildren && (
          <div className="transition-all duration-200">
            {node.children!.map((child) => renderNode(child, level + 1))}
          </div>
        )}
      </div>
    )
  }

  const expandAll = () => {
    const allPaths = new Set<string>()
    const collectPaths = (node: ProjectStructureType) => {
      if (node.type === 'folder' && node.children) {
        allPaths.add(node.path)
        node.children.forEach(collectPaths)
      }
    }
    collectPaths(structure)
    setExpandedNodes(allPaths)
  }

  const collapseAll = () => {
    setExpandedNodes(new Set())
  }

  return (
    <div className={`project-structure-tree ${className}`}>
      {/* 标题和操作栏 */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold mb-2">项目结构</h2>
          <p className="text-sm opacity-60">查看代码文件组织方式</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={expandAll}
            className="text-sm px-3 py-1.5 border border-white/20 hover:bg-white/10 transition-colors"
          >
            全部展开
          </button>
          <button
            onClick={collapseAll}
            className="text-sm px-3 py-1.5 border border-white/20 hover:bg-white/10 transition-colors"
          >
            全部折叠
          </button>
        </div>
      </div>

      {/* 树形结构 */}
      <div className="border border-white/20 p-4 max-h-[600px] overflow-y-auto bg-white/5">
        {renderNode(structure)}
      </div>

      {/* 统计信息 */}
      <div className="mt-4 flex items-center gap-6 text-sm opacity-60">
        <div className="flex items-center gap-2">
          <Folder className="w-4 h-4" />
          <span>文件夹: {countFolders(structure)}</span>
        </div>
        <div className="flex items-center gap-2">
          <File className="w-4 h-4" />
          <span>文件: {countFiles(structure)}</span>
        </div>
      </div>
    </div>
  )
}

// 辅助函数：统计文件夹数量
function countFolders(node: ProjectStructureType): number {
  let count = node.type === 'folder' ? 1 : 0
  if (node.children) {
    count += node.children.reduce((sum, child) => sum + countFolders(child), 0)
  }
  return count
}

// 辅助函数：统计文件数量
function countFiles(node: ProjectStructureType): number {
  let count = node.type === 'file' ? 1 : 0
  if (node.children) {
    count += node.children.reduce((sum, child) => sum + countFiles(child), 0)
  }
  return count
}
