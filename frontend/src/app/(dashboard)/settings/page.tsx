"use client";

import { TopNav } from "@/components/layout/top-nav";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Calendar, MessageSquare, Mail, Users } from "lucide-react";

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

export default function SettingsPage() {
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

          <TabsContent value="templates" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Email Templates</CardTitle>
                <CardDescription>
                  Customize the email templates used during onboarding.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">Coming soon...</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="team" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Team Members</CardTitle>
                <CardDescription>
                  Manage who has access to the onboarding platform.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">Coming soon...</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="account" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Account Settings</CardTitle>
                <CardDescription>
                  Manage your account preferences and security.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">Coming soon...</p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
