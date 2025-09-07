"use client"

import { useTheme } from "./theme-provider"
import { Button } from "./ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "./ui/dropdown-menu"
import { Palette } from "lucide-react"

export function ThemeSwitcher() {
  const { theme, setTheme } = useTheme()

  const themes = [
    { value: "default", label: "Default", color: "bg-cyan-500" },
    { value: "dark", label: "Dark", color: "bg-gray-900" },
    { value: "blue", label: "Blue", color: "bg-blue-600" },
    { value: "green", label: "Green", color: "bg-emerald-600" },
  ] as const

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2 bg-transparent">
          <Palette className="h-4 w-4" />
          Theme
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {themes.map((themeOption) => (
          <DropdownMenuItem key={themeOption.value} onClick={() => setTheme(themeOption.value)} className="gap-2">
            <div className={`w-3 h-3 rounded-full ${themeOption.color}`} />
            {themeOption.label}
            {theme === themeOption.value && " ✓"}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
