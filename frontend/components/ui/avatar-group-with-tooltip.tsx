"use client"

import * as React from "react"
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"

const DEFAULT_AVATARS = [
  {
    src: "https://randomuser.me/api/portraits/men/32.jpg",
    alt: "John Doe",
    name: "John Doe",
    initials: "JD",
  },
  {
    src: "https://randomuser.me/api/portraits/women/44.jpg",
    alt: "Sarah Smith",
    name: "Sarah Smith",
    initials: "SS",
  },
  {
    src: "https://randomuser.me/api/portraits/men/91.jpg",
    alt: "Alex Wong",
    name: "Alex Wong",
    initials: "AW",
  },
  {
    src: "https://randomuser.me/api/portraits/women/17.jpg",
    alt: "Emma Johnson",
    name: "Emma Johnson",
    initials: "EJ",
  },
]

export function AvatarGroupWithTooltips() {
  return (
    <TooltipProvider delayDuration={300}>
      <div className="flex items-center justify-center rounded-full border border-white/10 bg-white/5 p-1">
        <div className="flex items-center relative">
          {DEFAULT_AVATARS.map((avatar, index) => (
            <Tooltip key={index}>
              <TooltipTrigger asChild>
                <div className={cn("relative hover:z-10", index > 0 && "-ml-2")}>
                  <Avatar className="transition-all duration-300 hover:scale-105 hover:-translate-y-1 hover:shadow-lg border-2 border-dark-950 h-8 w-8">
                    <AvatarImage src={avatar.src} alt={avatar.alt} />
                    <AvatarFallback>{avatar.initials}</AvatarFallback>
                  </Avatar>
                </div>
              </TooltipTrigger>
              <TooltipContent side="bottom" className="font-medium text-xs">
                {avatar.name}
              </TooltipContent>
            </Tooltip>
          ))}
        </div>
      </div>
    </TooltipProvider>
  )
}
