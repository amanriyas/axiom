"use client";

import { useEffect, useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import {
  Upload,
  FileText,
  Trash2,
  X,
  Loader2,
  Check,
  AlertCircle,
  Download,
  Eye,
  RefreshCw,
} from "lucide-react";
import { TopNav } from "@/components/layout/top-nav";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { policyApi } from "@/lib/api";
import { Policy } from "@/types";

function formatFileSize(bytes: number | null): string {
  if (!bytes) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function PoliciesPage() {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [policyToDelete, setPolicyToDelete] = useState<Policy | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [reembedding, setReembedding] = useState<number | null>(null);

  // Upload form state
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [policyTitle, setPolicyTitle] = useState("");

  useEffect(() => {
    fetchPolicies();
  }, []);

  const fetchPolicies = async () => {
    try {
      const data = await policyApi.list();
      setPolicies(data);
    } catch (error) {
      console.error("Failed to fetch policies:", error);
      toast.error("Failed to load policies");
    } finally {
      setLoading(false);
    }
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setPdfFile(file);
      // Auto-fill title from filename (without extension)
      if (!policyTitle) {
        const nameWithoutExt = file.name.replace(/\.pdf$/i, "");
        setPolicyTitle(nameWithoutExt);
      }
    }
  }, [policyTitle]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  const handleUpload = async () => {
    if (!pdfFile || !policyTitle.trim()) {
      toast.error("Please provide a title and select a PDF file");
      return;
    }

    setIsSubmitting(true);
    try {
      await policyApi.upload(policyTitle.trim(), pdfFile);
      toast.success("Policy uploaded successfully");
      closeUploadDialog();
      fetchPolicies();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to upload policy";
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!policyToDelete) return;

    setIsSubmitting(true);
    try {
      await policyApi.delete(policyToDelete.id);
      toast.success("Policy deleted successfully");
      setDeleteDialogOpen(false);
      setPolicyToDelete(null);
      fetchPolicies();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to delete policy";
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const closeUploadDialog = () => {
    setUploadDialogOpen(false);
    setPdfFile(null);
    setPolicyTitle("");
  };

  const handleReembed = async (policyId: number) => {
    setReembedding(policyId);
    try {
      await policyApi.reembed(policyId);
      toast.success("Policy re-embedded successfully");
      fetchPolicies();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Re-embedding failed";
      toast.error(message);
    } finally {
      setReembedding(null);
    }
  };

  const handleViewPdf = (policy: Policy) => {
    const token = localStorage.getItem("access_token");
    const url = policyApi.getDownloadUrl(policy.id);
    // Open in new tab — the browser will render the PDF
    const w = window.open("", "_blank");
    if (w) {
      // Fetch with auth then display
      fetch(url, { headers: token ? { Authorization: `Bearer ${token}` } : {} })
        .then((res) => res.blob())
        .then((blob) => {
          const blobUrl = URL.createObjectURL(blob);
          w.location.href = blobUrl;
        })
        .catch(() => {
          w.close();
          toast.error("Failed to open PDF");
        });
    }
  };

  const handleDownloadPdf = async (policy: Policy) => {
    try {
      const token = localStorage.getItem("access_token");
      const url = policyApi.getDownloadUrl(policy.id);
      const res = await fetch(url, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error("Download failed");
      const blob = await res.blob();
      const blobUrl = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = blobUrl;
      a.download = policy.filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(blobUrl);
    } catch {
      toast.error("Failed to download PDF");
    }
  };

  return (
    <div className="flex flex-col">
      <TopNav title="Policy Documents" />

      <div className="flex-1 space-y-6 p-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div />
          <Button onClick={() => setUploadDialogOpen(true)}>
            <Upload className="mr-2 h-4 w-4" />
            Upload PDF
          </Button>
        </div>

        {/* Drop Zone */}
        <div
          {...getRootProps()}
          className={`flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-12 transition-colors cursor-pointer ${
            isDragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-muted-foreground/50"
          }`}
        >
          <input {...getInputProps()} />
          <FileText className="mb-4 h-12 w-12 text-muted-foreground" />
          <p className="text-center text-muted-foreground">
            {isDragActive
              ? "Drop the PDF file here..."
              : "Drag & drop PDF files here, or click to browse"}
          </p>
          <p className="mt-2 text-sm text-muted-foreground">
            PDF files only, up to 50MB
          </p>
        </div>

        {/* Policies Table */}
        <Card>
          <CardContent className="p-0">
            {loading ? (
              <div className="space-y-3 p-6">
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} className="h-12" />
                ))}
              </div>
            ) : policies.length === 0 ? (
              <div className="py-12 text-center text-muted-foreground">
                No policy documents yet. Upload your first PDF to get started.
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Document</TableHead>
                    <TableHead>Uploaded</TableHead>
                    <TableHead>Size</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {policies.map((policy) => (
                    <TableRow key={policy.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <FileText className="h-5 w-5 text-primary" />
                          <div>
                            <p className="font-medium">{policy.title}</p>
                            <p className="text-sm text-muted-foreground">
                              {policy.filename}
                            </p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {new Date(policy.uploaded_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {formatFileSize(policy.file_size)}
                      </TableCell>
                      <TableCell>
                        {policy.is_embedded ? (
                          <span className="inline-flex items-center gap-1.5 text-sm text-[#22c55e]" title="Document has been indexed and is available for RAG queries">
                            <Check className="h-4 w-4" />
                            Indexed
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 text-sm text-[#ef4444]" title="Embedding failed — document text could not be extracted or Voyage AI was unreachable. Click Re-embed to retry.">
                            <AlertCircle className="h-4 w-4" />
                            Not Indexed
                          </span>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            title="View PDF"
                            onClick={() => handleViewPdf(policy)}
                          >
                            <Eye className="h-4 w-4 text-muted-foreground" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            title="Download PDF"
                            onClick={() => handleDownloadPdf(policy)}
                          >
                            <Download className="h-4 w-4 text-muted-foreground" />
                          </Button>
                          {!policy.is_embedded && (
                            <Button
                              variant="ghost"
                              size="icon"
                              title="Re-embed for RAG"
                              disabled={reembedding === policy.id}
                              onClick={() => handleReembed(policy.id)}
                            >
                              {reembedding === policy.id ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                <RefreshCw className="h-4 w-4 text-muted-foreground" />
                              )}
                            </Button>
                          )}
                          <Button
                            variant="ghost"
                            size="icon"
                            title="Delete"
                            onClick={() => {
                              setPolicyToDelete(policy);
                              setDeleteDialogOpen(true);
                            }}
                          >
                            <Trash2 className="h-4 w-4 text-muted-foreground hover:text-destructive" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Upload Dialog */}
      <Dialog open={uploadDialogOpen} onOpenChange={closeUploadDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Upload Policy Document</DialogTitle>
            <DialogDescription>
              Upload a PDF document to be used for RAG-based document generation.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="title">Document Title</Label>
              <Input
                id="title"
                value={policyTitle}
                onChange={(e) => setPolicyTitle(e.target.value)}
                placeholder="Engineering Guidelines"
              />
            </div>

            {!pdfFile ? (
              <div
                {...getRootProps()}
                className={`flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-6 transition-colors cursor-pointer ${
                  isDragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25"
                }`}
              >
                <input {...getInputProps()} />
                <FileText className="mb-2 h-8 w-8 text-muted-foreground" />
                <p className="text-center text-sm text-muted-foreground">
                  Drop PDF here or click to browse
                </p>
              </div>
            ) : (
              <div className="rounded-lg border p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <FileText className="h-8 w-8 text-primary" />
                    <div>
                      <p className="font-medium">{pdfFile.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {(pdfFile.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setPdfFile(null)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}

            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={closeUploadDialog}>
                Cancel
              </Button>
              <Button onClick={handleUpload} disabled={!pdfFile || !policyTitle.trim() || isSubmitting}>
                {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Upload
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Policy</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete &quot;{policyToDelete?.title}&quot;? This will also remove its embeddings from the vector store.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {isSubmitting ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : null}
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
