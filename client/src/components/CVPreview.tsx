type Props = {
    jsonData: string;
  };
  
  export default function CVPreview({ jsonData }: Props) {
    if (!jsonData) return null;
  
    return (
      <div className="mt-6">
        <h2 className="text-lg font-semibold">Generated JSON</h2>
        <pre className="bg-gray-100 p-4 rounded text-sm whitespace-pre-wrap">{jsonData}</pre>
      </div>
    );
  }
  