import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Plus, RefreshCw, ShoppingCart, Check, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { shoppingListsApi } from "@/api/shopping-lists";
import type { ShoppingListCreate } from "@/types";

function healthPriorityBadge(score: number | null | undefined) {
  if (score == null) return null;
  if (score >= 0.7)
    return (
      <Badge variant="secondary" className="text-xs bg-green-500/10 text-green-600">
        High Priority
      </Badge>
    );
  if (score >= 0.4)
    return (
      <Badge variant="secondary" className="text-xs bg-yellow-500/10 text-yellow-600">
        Medium
      </Badge>
    );
  return (
    <Badge variant="secondary" className="text-xs text-muted-foreground">
      Low
    </Badge>
  );
}

export function ShoppingListPage() {
  const queryClient = useQueryClient();
  const [createOpen, setCreateOpen] = useState(false);
  const [newList, setNewList] = useState<ShoppingListCreate>({ name: "", items: [] });
  const [newItemName, setNewItemName] = useState("");

  const { data: lists = [] } = useQuery({
    queryKey: ["shopping-lists"],
    queryFn: shoppingListsApi.list,
  });

  const createMutation = useMutation({
    mutationFn: shoppingListsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["shopping-lists"] });
      setCreateOpen(false);
      setNewList({ name: "", items: [] });
      toast.success("Shopping list created");
    },
  });

  const replenishMutation = useMutation({
    mutationFn: shoppingListsApi.replenish,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["shopping-lists"] });
      toast.success("Low-stock items added");
    },
  });

  const addItemToNewList = () => {
    if (!newItemName.trim()) return;
    setNewList({
      ...newList,
      items: [...(newList.items || []), { name: newItemName.trim() }],
    });
    setNewItemName("");
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Shopping Lists</h1>
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New List
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Shopping List</DialogTitle>
            </DialogHeader>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                createMutation.mutate(newList);
              }}
              className="space-y-4"
            >
              <div className="space-y-2">
                <Label>List Name</Label>
                <Input
                  value={newList.name}
                  onChange={(e) => setNewList({ ...newList, name: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label>Add Items</Label>
                <div className="flex gap-2">
                  <Input
                    value={newItemName}
                    onChange={(e) => setNewItemName(e.target.value)}
                    placeholder="Item name"
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        addItemToNewList();
                      }
                    }}
                  />
                  <Button type="button" variant="outline" onClick={addItemToNewList}>
                    Add
                  </Button>
                </div>
                {newList.items && newList.items.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {newList.items.map((item, i) => (
                      <Badge key={i} variant="secondary">
                        {item.name}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
              <Button type="submit" className="w-full" disabled={createMutation.isPending}>
                Create List
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="space-y-4">
        {lists.map((list) => (
          <Card key={list.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <ShoppingCart className="h-5 w-5" />
                  {list.name}
                  <Badge variant="outline">{list.status}</Badge>
                </CardTitle>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => replenishMutation.mutate(list.id)}
                    disabled={replenishMutation.isPending}
                  >
                    <RefreshCw className="h-4 w-4 mr-1" />
                    Replenish
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={async () => {
                      const { url } = await shoppingListsApi.getAmazonCartUrl(list.id);
                      if (url) window.open(url, "_blank");
                      else toast.info("No unchecked items");
                    }}
                  >
                    <ExternalLink className="h-4 w-4 mr-1" />
                    Amazon
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {list.items.length > 0 ? (
                <ul className="space-y-2">
                  {[...list.items]
                    .sort(
                      (a, b) =>
                        (b.health_priority_score ?? 0) -
                        (a.health_priority_score ?? 0)
                    )
                    .map((item) => (
                    <li
                      key={item.id}
                      className={`flex items-center gap-3 p-2 rounded ${
                        item.is_checked ? "opacity-50" : ""
                      }`}
                    >
                      <div
                        className={`h-5 w-5 rounded border-2 flex items-center justify-center ${
                          item.is_checked
                            ? "bg-primary border-primary"
                            : "border-muted-foreground"
                        }`}
                      >
                        {item.is_checked && <Check className="h-3 w-3 text-primary-foreground" />}
                      </div>
                      <span className={item.is_checked ? "line-through" : ""}>
                        {item.name}
                        {item.quantity && ` (${item.quantity} ${item.unit || ""})`}
                      </span>
                      {item.is_ai_suggested && (
                        <Badge variant="secondary" className="text-xs">
                          AI
                        </Badge>
                      )}
                      {healthPriorityBadge(item.health_priority_score)}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-muted-foreground text-sm">No items in this list</p>
              )}
            </CardContent>
          </Card>
        ))}

        {lists.length === 0 && (
          <p className="text-center text-muted-foreground py-12">
            No shopping lists yet. Create one to get started!
          </p>
        )}
      </div>
    </div>
  );
}
