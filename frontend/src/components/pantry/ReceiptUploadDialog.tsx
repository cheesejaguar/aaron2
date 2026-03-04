import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Receipt } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { pantryApi } from "@/api/pantry";

export function ReceiptUploadDialog() {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [rawText, setRawText] = useState("");

  const mutation = useMutation({
    mutationFn: pantryApi.parseReceipt,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["pantry"] });
      setOpen(false);
      setRawText("");
      toast.success(`Added ${data.pantry_items_created} items from receipt`);
    },
    onError: () => toast.error("Failed to parse receipt"),
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="gap-2 rounded-xl h-10 px-4 border-border/50">
          <Receipt className="h-4 w-4" />
          Upload Receipt
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md rounded-2xl">
        <DialogHeader>
          <DialogTitle
            className="text-xl"
            style={{ fontFamily: "'DM Serif Display', serif" }}
          >
            Parse Grocery Receipt
          </DialogTitle>
        </DialogHeader>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            mutation.mutate(rawText);
          }}
          className="space-y-4 mt-2"
        >
          <div className="space-y-2">
            <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
              Paste receipt text
            </label>
            <textarea
              className="w-full min-h-[200px] rounded-xl border border-border/40 bg-muted/20 px-4 py-3 text-sm font-light focus:bg-background focus:border-border/70 transition-colors outline-none resize-none"
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              placeholder="Paste your grocery receipt text here..."
              required
            />
          </div>
          <Button
            type="submit"
            className="w-full rounded-xl h-10"
            disabled={mutation.isPending}
          >
            {mutation.isPending ? "Parsing..." : "Parse Receipt"}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
