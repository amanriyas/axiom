"use client";

import { useState } from "react";
import { TopNav } from "@/components/layout/top-nav";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useAuth } from "@/hooks/use-auth";
import { toast } from "sonner";
import {
  Calendar,
  MessageSquare,
  Mail,
  Users,
  FileText,
  ClipboardList,
  Monitor,
  Shield,
  Save,
  RotateCcw,
  Eye,
  EyeOff,
  Crown,
  UserCog,
} from "lucide-react";

// ── Integrations ──

const integrations = [
  {
    id: "google-calendar",
    name: "Google Calendar",
    description: "Schedule orientation, 1:1s, buddy meetups",
    icon: Calendar,
    connected: false,
    comingSoon: false,
  },
  {
    id: "slack",
    name: "Slack",
    description: "Send onboarding notifications",
    icon: MessageSquare,
    connected: false,
    comingSoon: true,
  },
  {
    id: "microsoft-365",
    name: "Microsoft 365",
    description: "Sync with Outlook calendar and Teams",
    icon: Mail,
    connected: false,
    comingSoon: true,
  },
  {
    id: "bamboohr",
    name: "BambooHR",
    description: "Sync employee data from HR system",
    icon: Users,
    connected: false,
    comingSoon: true,
  },
];

// ── Onboarding document templates (mirrors backend prompts/templates.py) ──

interface OnboardingTemplate {
  id: string;
  name: string;
  description: string;
  icon: typeof Mail;
  prompt: string;
}

const DEFAULT_TEMPLATES: OnboardingTemplate[] = [
  {
    id: "welcome_email",
    name: "Welcome Email",
    description:
      "Warm onboarding email sent to new hires confirming their first day, introducing their manager and buddy, and outlining the first-week schedule.",
    icon: Mail,
    prompt: `Generate a warm, professional welcome email for a new employee joining the team.

The email should:
1. Welcome them enthusiastically to the team
2. Confirm their start date and first-day schedule
3. Introduce their manager and buddy by name
4. List what to expect during their first week:
   - Day 1: Orientation, IT setup, team introductions
   - Day 2: Manager 1:1, tool walkthroughs
   - Day 3: Buddy meetup, department deep-dive
5. Provide practical tips (dress code, parking, what to bring)
6. Include contact information for questions
7. End with an encouraging closing

Format as a complete email with Subject line, greeting, body, and sign-off.`,
  },
  {
    id: "offer_letter",
    name: "Offer Letter",
    description:
      "Formal employment confirmation letter covering position details, compensation, benefits overview, and employment terms.",
    icon: FileText,
    prompt: `Generate a formal offer letter / employment confirmation.

The offer letter should include:
1. A formal header with company details
2. Position title and department confirmation
3. Start date and reporting structure
4. A section for compensation details
5. Benefits overview (health insurance, PTO, retirement plan)
6. Employment terms (at-will employment, probationary period)
7. Confidentiality and IP agreement reference
8. Acceptance instructions and signature block
9. A warm closing expressing excitement about them joining

Use a formal but welcoming tone. Format as a professional business letter.`,
  },
  {
    id: "plan_30_60_90",
    name: "30-60-90 Day Plan",
    description:
      "Structured onboarding plan with milestones for the first 30, 60, and 90 days tailored to the employee's role and department.",
    icon: ClipboardList,
    prompt: `Create a comprehensive 30-60-90 day onboarding plan tailored to the role.

Structure the plan as follows:

First 30 Days — Learn & Orient
- Specific learning objectives for the role
- Key people to meet and relationships to build
- Training modules and documentation to review
- Tools and systems to master
- Weekly check-in milestones

Days 31-60 — Contribute & Collaborate
- Initial project assignments appropriate for the role
- Cross-functional collaboration opportunities
- Skill development goals
- Feedback checkpoints with manager

Days 61-90 — Own & Deliver
- Independent project ownership
- Performance metrics and success criteria
- Team presentation or knowledge sharing
- Goal setting for the next quarter
- 90-day review preparation

Include 4-6 concrete action items per phase.`,
  },
  {
    id: "equipment_request",
    name: "Equipment Request",
    description:
      "IT provisioning checklist covering hardware, software licenses, cloud access, and setup timeline for the new hire.",
    icon: Monitor,
    prompt: `Generate an IT equipment and software provisioning request.

Create a detailed provisioning checklist including:

Hardware:
- Primary workstation (laptop vs desktop based on role)
- Monitors and peripherals
- Mobile device if applicable
- Any role-specific hardware

Software & Licenses:
- Standard suite (email, calendar, chat, video conferencing)
- Department-specific tools
- Development tools if applicable
- Security software (VPN, MFA setup)

Access & Accounts:
- Email and directory setup
- Internal systems and dashboards
- Code repositories or document management
- Physical access (badge, office keys)

Timeline:
- What must be ready before Day 1
- What can be set up during the first week

Format as a structured IT request form with clear categories.`,
  },
  {
    id: "data_validation",
    name: "Data Validation",
    description:
      "Automated check that validates employee data completeness — verifies email format, department match, start date, and manager/buddy assignment.",
    icon: Shield,
    prompt: `Analyze and validate the new hire data. Summarize the employee profile and flag any missing or potentially incorrect information.

Provide a brief validation summary including:
1. Data completeness check
2. Any fields that need attention (e.g., missing manager or buddy)
3. A one-line readiness assessment`,
  },
];

// ── Team members (consistent with seeded employee data) ──

interface TeamMember {
  id: number;
  name: string;
  email: string;
  role: "admin" | "hr" | "viewer";
  lastActive: string;
}

const TEAM_MEMBERS: TeamMember[] = [
  {
    id: 100,
    name: "Rachel Green",
    email: "rachel.green@axiom.io",
    role: "admin",
    lastActive: "2 minutes ago",
  },
  {
    id: 101,
    name: "Sarah Kim",
    email: "sarah.kim@axiom.io",
    role: "hr",
    lastActive: "1 hour ago",
  },
  {
    id: 102,
    name: "David Lee",
    email: "david.lee@axiom.io",
    role: "hr",
    lastActive: "3 hours ago",
  },
  {
    id: 103,
    name: "Alex Chen",
    email: "alex.chen@axiom.io",
    role: "viewer",
    lastActive: "Yesterday",
  },
];

// ── Page Component ──

export default function SettingsPage() {
  const { user } = useAuth();

  // Templates state
  const [templates, setTemplates] = useState<OnboardingTemplate[]>(DEFAULT_TEMPLATES);
  const [editingTemplate, setEditingTemplate] = useState<string | null>(null);
  const [editBuffer, setEditBuffer] = useState("");
  const [expandedTemplate, setExpandedTemplate] = useState<string | null>(null);

  // Account state
  const [accountName, setAccountName] = useState(user?.name ?? "");
  const [accountEmail, setAccountEmail] = useState(user?.email ?? "");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showCurrentPw, setShowCurrentPw] = useState(false);
  const [showNewPw, setShowNewPw] = useState(false);

  // Team invite state
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<"hr" | "viewer">("hr");

  // Helpers
  const getInitials = (name: string) =>
    name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2);

  const roleBadgeVariant = (role: string) => {
    if (role === "admin") return "default" as const;
    if (role === "hr") return "secondary" as const;
    return "outline" as const;
  };

  // Template actions
  const startEditTemplate = (tpl: OnboardingTemplate) => {
    setEditingTemplate(tpl.id);
    setEditBuffer(tpl.prompt);
  };

  const saveTemplate = (id: string) => {
    setTemplates((prev) =>
      prev.map((t) => (t.id === id ? { ...t, prompt: editBuffer } : t))
    );
    setEditingTemplate(null);
    toast.success("Template saved");
  };

  const resetTemplate = (id: string) => {
    const original = DEFAULT_TEMPLATES.find((t) => t.id === id);
    if (original) {
      setTemplates((prev) =>
        prev.map((t) => (t.id === id ? { ...t, prompt: original.prompt } : t))
      );
      setEditingTemplate(null);
      toast.info("Template reset to default");
    }
  };

  const handleSaveProfile = () => {
    toast.success("Profile updated successfully");
  };

  const handleChangePassword = () => {
    if (!currentPassword) {
      toast.error("Please enter your current password");
      return;
    }
    if (newPassword.length < 8) {
      toast.error("New password must be at least 8 characters");
      return;
    }
    if (newPassword !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }
    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");
    toast.success("Password changed successfully");
  };

  const handleInvite = () => {
    if (!inviteEmail.includes("@")) {
      toast.error("Please enter a valid email address");
      return;
    }
    toast.success(`Invitation sent to ${inviteEmail}`);
    setInviteEmail("");
  };

  return (
    <div className="flex flex-col">
      <TopNav title="Settings" />

      <div className="flex-1 p-6">
        <Tabs defaultValue="integrations" className="space-y-6">
          <TabsList>
            <TabsTrigger value="integrations">Integrations</TabsTrigger>
            <TabsTrigger value="templates">Templates</TabsTrigger>
            <TabsTrigger value="team">Team</TabsTrigger>
            <TabsTrigger value="account">Account</TabsTrigger>
          </TabsList>

          {/* ━━━ INTEGRATIONS ━━━ */}
          <TabsContent value="integrations" className="space-y-4">
            {integrations.map((integration) => {
              const Icon = integration.icon;
              return (
                <Card key={integration.id}>
                  <CardContent className="flex items-center justify-between p-6">
                    <div className="flex items-center gap-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
                        <Icon className="h-6 w-6" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold">{integration.name}</h3>
                          {integration.comingSoon && (
                            <Badge variant="secondary" className="text-xs">
                              Coming soon
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {integration.description}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      {integration.connected && (
                        <span className="text-sm text-muted-foreground">
                          admin@company.com
                        </span>
                      )}
                      <Button
                        variant={integration.connected ? "outline" : "default"}
                        disabled={integration.comingSoon}
                      >
                        {integration.connected ? "Disconnect" : "Connect"}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </TabsContent>

          {/* ━━━ TEMPLATES ━━━ */}
          <TabsContent value="templates" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Onboarding Templates</CardTitle>
                <CardDescription>
                  Customize the AI prompts used to generate onboarding documents.
                  Changes apply to all future onboarding workflows.
                </CardDescription>
              </CardHeader>
            </Card>

            {templates.map((tpl) => {
              const Icon = tpl.icon;
              const isEditing = editingTemplate === tpl.id;
              const isExpanded = expandedTemplate === tpl.id;

              return (
                <Card key={tpl.id}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-start gap-4 flex-1">
                        <div className="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-muted">
                          <Icon className="h-5 w-5" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold">{tpl.name}</h3>
                          <p className="text-sm text-muted-foreground mt-1">
                            {tpl.description}
                          </p>

                          {(isExpanded || isEditing) && (
                            <div className="mt-4">
                              <Separator className="mb-4" />
                              {isEditing ? (
                                <Textarea
                                  value={editBuffer}
                                  onChange={(e) => setEditBuffer(e.target.value)}
                                  className="min-h-55 font-mono text-sm"
                                />
                              ) : (
                                <pre className="whitespace-pre-wrap text-sm text-muted-foreground font-mono bg-muted/50 rounded-lg p-4 max-h-75 overflow-y-auto">
                                  {tpl.prompt}
                                </pre>
                              )}
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        {isEditing ? (
                          <>
                            <Button size="sm" onClick={() => saveTemplate(tpl.id)}>
                              <Save className="h-4 w-4 mr-1" />
                              Save
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => setEditingTemplate(null)}
                            >
                              Cancel
                            </Button>
                          </>
                        ) : (
                          <>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() =>
                                setExpandedTemplate(isExpanded ? null : tpl.id)
                              }
                            >
                              {isExpanded ? (
                                <EyeOff className="h-4 w-4 mr-1" />
                              ) : (
                                <Eye className="h-4 w-4 mr-1" />
                              )}
                              {isExpanded ? "Hide" : "View"}
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => startEditTemplate(tpl)}
                            >
                              Edit
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => resetTemplate(tpl.id)}
                              title="Reset to default"
                            >
                              <RotateCcw className="h-4 w-4" />
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </TabsContent>

          {/* ━━━ TEAM ━━━ */}
          <TabsContent value="team" className="space-y-4">
            {/* Invite */}
            <Card>
              <CardHeader>
                <CardTitle>Invite Team Member</CardTitle>
                <CardDescription>
                  Add colleagues to the onboarding platform. They will receive
                  an email invitation to create their account.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-end gap-3">
                  <div className="flex-1">
                    <label className="text-sm font-medium mb-1.5 block">
                      Email address
                    </label>
                    <Input
                      type="email"
                      placeholder="colleague@axiom.io"
                      value={inviteEmail}
                      onChange={(e) => setInviteEmail(e.target.value)}
                    />
                  </div>
                  <div className="w-36">
                    <label className="text-sm font-medium mb-1.5 block">
                      Role
                    </label>
                    <select
                      value={inviteRole}
                      onChange={(e) =>
                        setInviteRole(e.target.value as "hr" | "viewer")
                      }
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                      <option value="hr">HR Manager</option>
                      <option value="viewer">Viewer</option>
                    </select>
                  </div>
                  <Button onClick={handleInvite}>Send Invite</Button>
                </div>
              </CardContent>
            </Card>

            {/* Current user */}
            {user && (
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <Avatar className="h-10 w-10">
                        <AvatarFallback className="bg-primary text-primary-foreground text-sm">
                          {getInitials(user.name)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-semibold">{user.name}</p>
                          <Badge variant="secondary" className="text-xs">
                            You
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {user.email}
                        </p>
                      </div>
                    </div>
                    <Badge variant={roleBadgeVariant(user.role)}>
                      <Crown className="h-3 w-3 mr-1" />
                      {user.role.toUpperCase()}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Team list */}
            {TEAM_MEMBERS.map((member) => (
              <Card key={member.id}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <Avatar className="h-10 w-10">
                        <AvatarFallback className="text-sm">
                          {getInitials(member.name)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-semibold">{member.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {member.email}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-xs text-muted-foreground">
                        {member.lastActive}
                      </span>
                      <Badge variant={roleBadgeVariant(member.role)}>
                        {member.role === "admin" && (
                          <Crown className="h-3 w-3 mr-1" />
                        )}
                        {member.role === "hr" && (
                          <UserCog className="h-3 w-3 mr-1" />
                        )}
                        {member.role === "viewer" && (
                          <Eye className="h-3 w-3 mr-1" />
                        )}
                        {member.role.toUpperCase()}
                      </Badge>
                      <Button size="sm" variant="ghost" className="text-xs">
                        Remove
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {/* ━━━ ACCOUNT ━━━ */}
          <TabsContent value="account" className="space-y-4">
            {/* Profile */}
            <Card>
              <CardHeader>
                <CardTitle>Profile</CardTitle>
                <CardDescription>
                  Your personal information associated with this account.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-4 mb-6">
                  <Avatar className="h-16 w-16">
                    <AvatarFallback className="bg-primary text-primary-foreground text-lg">
                      {user ? getInitials(user.name) : "?"}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-semibold text-lg">
                      {user?.name ?? "User"}
                    </p>
                    <Badge variant={roleBadgeVariant(user?.role ?? "viewer")}>
                      {user?.role?.toUpperCase() ?? "VIEWER"}
                    </Badge>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium mb-1.5 block">
                      Full Name
                    </label>
                    <Input
                      value={accountName}
                      onChange={(e) => setAccountName(e.target.value)}
                      placeholder="Your name"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1.5 block">
                      Email Address
                    </label>
                    <Input
                      value={accountEmail}
                      onChange={(e) => setAccountEmail(e.target.value)}
                      placeholder="you@company.com"
                    />
                  </div>
                </div>

                <div className="flex justify-end pt-2">
                  <Button onClick={handleSaveProfile}>
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Change Password */}
            <Card>
              <CardHeader>
                <CardTitle>Change Password</CardTitle>
                <CardDescription>
                  Update your password. You will stay logged in on this device.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-1.5 block">
                    Current Password
                  </label>
                  <div className="relative">
                    <Input
                      type={showCurrentPw ? "text" : "password"}
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      placeholder="Enter current password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowCurrentPw(!showCurrentPw)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showCurrentPw ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium mb-1.5 block">
                      New Password
                    </label>
                    <div className="relative">
                      <Input
                        type={showNewPw ? "text" : "password"}
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        placeholder="At least 8 characters"
                      />
                      <button
                        type="button"
                        onClick={() => setShowNewPw(!showNewPw)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                      >
                        {showNewPw ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1.5 block">
                      Confirm New Password
                    </label>
                    <Input
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Repeat new password"
                    />
                  </div>
                </div>

                <div className="flex justify-end pt-2">
                  <Button variant="outline" onClick={handleChangePassword}>
                    Change Password
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Danger Zone */}
            <Card className="border-destructive/50">
              <CardHeader>
                <CardTitle className="text-destructive">Danger Zone</CardTitle>
                <CardDescription>
                  Irreversible actions that affect your account.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Delete Account</p>
                    <p className="text-sm text-muted-foreground">
                      Permanently remove your account and all associated data.
                      This action cannot be undone.
                    </p>
                  </div>
                  <Button
                    variant="destructive"
                    onClick={() =>
                      toast.error("Account deletion is disabled for this demo.")
                    }
                  >
                    Delete Account
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
