"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Bell,
  Search,
  LogOut,
  Users,
  FileText,
  Workflow,
  X,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/hooks/use-auth";
import { authApi, employeeApi, policyApi } from "@/lib/api";
import type { Notification, Employee, Policy } from "@/types";

interface TopNavProps {
  title: string;
}

// Search result types
interface SearchResult {
  id: string;
  title: string;
  subtitle: string;
  type: "employee" | "policy";
  href: string;
}

export function TopNav({ title }: TopNavProps) {
  const { user, logout } = useAuth();
  const router = useRouter();

  // Notifications state
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [notifOpen, setNotifOpen] = useState(false);
  const [notifLoading, setNotifLoading] = useState(false);
  const [readIds, setReadIds] = useState<Set<string>>(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("axiom_read_notifications");
      return stored ? new Set(JSON.parse(stored)) : new Set();
    }
    return new Set();
  });

  // Search state
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchData, setSearchData] = useState<{
    employees: Employee[];
    policies: Policy[];
  } | null>(null);
  const searchRef = useRef<HTMLDivElement>(null);
  const notifRef = useRef<HTMLDivElement>(null);

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  // Fetch notifications
  const fetchNotifications = useCallback(async () => {
    setNotifLoading(true);
    try {
      const data = await authApi.notifications();
      setNotifications(data);
    } catch {
      console.error("Failed to fetch notifications");
    } finally {
      setNotifLoading(false);
    }
  }, []);

  // Load notifications on mount (only when authenticated)
  useEffect(() => {
    if (user) fetchNotifications();
  }, [user, fetchNotifications]);

  // Persist read IDs
  useEffect(() => {
    localStorage.setItem(
      "axiom_read_notifications",
      JSON.stringify([...readIds])
    );
  }, [readIds]);

  // Calculate unread count
  const unreadCount = notifications.filter((n) => !readIds.has(n.id)).length;

  const markAllRead = () => {
    const allIds = new Set(notifications.map((n) => n.id));
    setReadIds(allIds);
  };

  const markOneRead = (id: string) => {
    setReadIds((prev) => new Set([...prev, id]));
  };

  // Notification icon based on type
  const getNotifIcon = (type: string) => {
    switch (type) {
      case "onboarding":
        return <Workflow className="h-4 w-4 text-blue-500 shrink-0" />;
      case "employee":
        return <Users className="h-4 w-4 text-green-500 shrink-0" />;
      case "policy":
        return <FileText className="h-4 w-4 text-orange-500 shrink-0" />;
      default:
        return <Bell className="h-4 w-4 text-muted-foreground shrink-0" />;
    }
  };

  // Format relative time
  const formatRelativeTime = (timestamp: string) => {
    const diff = Date.now() - new Date(timestamp).getTime();
    const minutes = Math.floor(diff / 60000);
    if (minutes < 1) return "just now";
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  // Search: Fetch data lazily on first focus
  const loadSearchData = useCallback(async () => {
    if (searchData) return;
    try {
      const [employees, policies] = await Promise.all([
        employeeApi.list(),
        policyApi.list(),
      ]);
      setSearchData({ employees, policies });
    } catch {
      console.error("Failed to load search data");
    }
  }, [searchData]);

  // Filter search results
  useEffect(() => {
    if (!searchQuery.trim() || !searchData) {
      setSearchResults([]);
      return;
    }
    const q = searchQuery.toLowerCase();
    const results: SearchResult[] = [];

    // Search employees
    searchData.employees.forEach((emp) => {
      const match =
        emp.name.toLowerCase().includes(q) ||
        emp.email.toLowerCase().includes(q) ||
        emp.department.toLowerCase().includes(q) ||
        emp.role.toLowerCase().includes(q);
      if (match) {
        results.push({
          id: `emp-${emp.id}`,
          title: emp.name,
          subtitle: `${emp.role} · ${emp.department}`,
          type: "employee",
          href: "/employees",
        });
      }
    });

    // Search policies
    searchData.policies.forEach((pol) => {
      const match =
        pol.title.toLowerCase().includes(q) ||
        pol.filename.toLowerCase().includes(q);
      if (match) {
        results.push({
          id: `pol-${pol.id}`,
          title: pol.title,
          subtitle: pol.filename,
          type: "policy",
          href: "/policies",
        });
      }
    });

    setSearchResults(results.slice(0, 8));
  }, [searchQuery, searchData]);

  // Close search/notif on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setSearchOpen(false);
      }
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) {
        setNotifOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-background px-6">
      <h1 className="text-xl font-semibold">{title}</h1>

      <div className="flex items-center gap-4">
        {/* Search */}
        <div className="relative" ref={searchRef}>
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search employees, policies..."
            className="w-72 pl-9 pr-8"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setSearchOpen(true);
            }}
            onFocus={() => {
              loadSearchData();
              if (searchQuery.trim()) setSearchOpen(true);
            }}
          />
          {searchQuery && (
            <button
              onClick={() => {
                setSearchQuery("");
                setSearchOpen(false);
              }}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          )}

          {/* Search Results Dropdown */}
          {searchOpen && searchQuery.trim() && (
            <div className="absolute right-0 top-full mt-1 w-80 rounded-lg border border-border bg-popover shadow-lg z-50">
              <div className="p-2 border-b border-border">
                <p className="text-xs text-muted-foreground font-medium px-2">
                  {searchResults.length} result
                  {searchResults.length !== 1 ? "s" : ""} for &quot;
                  {searchQuery}&quot;
                </p>
              </div>
              <ScrollArea className="max-h-64">
                {searchResults.length === 0 ? (
                  <div className="p-4 text-center text-sm text-muted-foreground">
                    No results found
                  </div>
                ) : (
                  <div className="p-1">
                    {searchResults.map((result) => (
                      <button
                        key={result.id}
                        onClick={() => {
                          router.push(result.href);
                          setSearchOpen(false);
                          setSearchQuery("");
                        }}
                        className="flex items-center gap-3 w-full rounded-md px-3 py-2 text-left hover:bg-accent transition-colors"
                      >
                        {result.type === "employee" ? (
                          <Users className="h-4 w-4 text-green-500 shrink-0" />
                        ) : (
                          <FileText className="h-4 w-4 text-orange-500 shrink-0" />
                        )}
                        <div className="min-w-0">
                          <p className="text-sm font-medium truncate">
                            {result.title}
                          </p>
                          <p className="text-xs text-muted-foreground truncate">
                            {result.subtitle}
                          </p>
                        </div>
                        <Badge
                          variant="outline"
                          className="ml-auto text-[10px] shrink-0"
                        >
                          {result.type}
                        </Badge>
                      </button>
                    ))}
                  </div>
                )}
              </ScrollArea>
            </div>
          )}
        </div>

        {/* Notifications */}
        <div className="relative" ref={notifRef}>
          <button
            onClick={() => {
              setNotifOpen((prev) => !prev);
              if (!notifOpen) fetchNotifications();
            }}
            className="relative flex h-9 w-9 items-center justify-center rounded-md hover:bg-accent"
          >
            <Bell className="h-5 w-5" />
            {unreadCount > 0 && (
              <span className="absolute right-1 top-1 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[10px] text-primary-foreground">
                {unreadCount > 9 ? "9+" : unreadCount}
              </span>
            )}
          </button>

          {/* Notifications Dropdown */}
          {notifOpen && (
            <div className="absolute right-0 top-full mt-1 w-96 rounded-lg border border-border bg-popover shadow-lg z-50">
              <div className="flex items-center justify-between p-3 border-b border-border">
                <h3 className="text-sm font-semibold">Notifications</h3>
                {unreadCount > 0 && (
                  <button
                    onClick={markAllRead}
                    className="text-xs text-primary hover:underline"
                  >
                    Mark all read
                  </button>
                )}
              </div>
              <div className="max-h-80 overflow-y-auto">
                {notifLoading ? (
                  <div className="p-4 text-center text-sm text-muted-foreground">
                    Loading...
                  </div>
                ) : notifications.length === 0 ? (
                  <div className="p-8 text-center">
                    <Bell className="h-8 w-8 mx-auto text-muted-foreground/30 mb-2" />
                    <p className="text-sm text-muted-foreground">
                      No notifications yet
                    </p>
                  </div>
                ) : (
                  <div className="p-1">
                    {notifications.map((notif) => {
                      const isRead = readIds.has(notif.id);
                      return (
                        <button
                          key={notif.id}
                          onClick={() => markOneRead(notif.id)}
                          className={`flex items-start gap-3 w-full rounded-md px-3 py-2.5 text-left hover:bg-accent transition-colors ${
                            !isRead ? "bg-accent/40" : ""
                          }`}
                        >
                          <div className="mt-0.5">{getNotifIcon(notif.type)}</div>
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center gap-2">
                              <p
                                className={`text-sm truncate ${
                                  !isRead ? "font-semibold" : "font-medium"
                                }`}
                              >
                                {notif.title}
                              </p>
                              {!isRead && (
                                <span className="h-2 w-2 rounded-full bg-primary shrink-0" />
                              )}
                            </div>
                            <p className="text-xs text-muted-foreground line-clamp-2 mt-0.5">
                              {notif.description}
                            </p>
                            <p className="text-[11px] text-muted-foreground/70 mt-1">
                              {formatRelativeTime(notif.timestamp)}
                            </p>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
              {notifications.length > 0 && (
                <div className="border-t border-border p-2">
                  <p className="text-xs text-center text-muted-foreground">
                    Showing latest {notifications.length} notifications
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* User Menu */}
        {user && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="flex items-center gap-2 rounded-md px-2 py-1 hover:bg-accent">
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                    {getInitials(user.name)}
                  </AvatarFallback>
                </Avatar>
                <span className="text-sm font-medium">{user.name}</span>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              <div className="px-2 py-1.5">
                <p className="text-sm font-medium">{user.name}</p>
                <p className="text-xs text-muted-foreground">{user.email}</p>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={logout} className="text-destructive">
                <LogOut className="mr-2 h-4 w-4" />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>
    </header>
  );
}
