"use client";

import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import { TrendingUp, TrendingDown } from "lucide-react";

interface StatsCardProps {
  title: string;
  value: string | number;
  trend?: number;
  trendLabel?: string;
  icon?: React.ReactNode;
  iconColor?: "emerald" | "blue" | "purple" | "orange" | "red";
  className?: string;
}

const iconColorClasses = {
  emerald: "bg-emerald-500/10 text-emerald-400 shadow-emerald-500/20",
  blue: "bg-blue-500/10 text-blue-400 shadow-blue-500/20",
  purple: "bg-purple-500/10 text-purple-400 shadow-purple-500/20",
  orange: "bg-orange-500/10 text-orange-400 shadow-orange-500/20",
  red: "bg-red-500/10 text-red-400 shadow-red-500/20",
};

export function StatsCard({
  title,
  value,
  trend,
  trendLabel,
  icon,
  iconColor = "emerald",
  className,
}: StatsCardProps) {
  const isPositive = trend !== undefined && trend > 0;
  const isNegative = trend !== undefined && trend < 0;

  return (
    <Card className={cn("overflow-hidden", className)}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="space-y-3">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-3xl font-bold tracking-tight">{value}</p>
            {trend !== undefined && (
              <div className="flex items-center gap-1.5 text-sm">
                {isPositive ? (
                  <div className="flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-0.5">
                    <TrendingUp className="h-3.5 w-3.5 text-emerald-400" />
                    <span className="text-emerald-400 text-xs font-medium">
                      +{trend}{trendLabel || ""}
                    </span>
                  </div>
                ) : isNegative ? (
                  <div className="flex items-center gap-1 rounded-full bg-red-500/10 px-2 py-0.5">
                    <TrendingDown className="h-3.5 w-3.5 text-red-400" />
                    <span className="text-red-400 text-xs font-medium">
                      {trend}{trendLabel || ""}
                    </span>
                  </div>
                ) : (
                  <span className="text-muted-foreground text-xs">
                    {trend}{trendLabel || ""}
                  </span>
                )}
              </div>
            )}
          </div>
          {icon && (
            <div
              className={cn(
                "rounded-xl p-3 shadow-lg transition-all duration-300",
                iconColorClasses[iconColor]
              )}
            >
              {icon}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
