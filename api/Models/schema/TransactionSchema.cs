using System.Text.Json.Serialization;
using MongoDB.Bson;

namespace api.Models.schema
{
    public class TransactionSchema
    {
        [JsonPropertyName("id")]
        public string Id { get; set; }
        [JsonPropertyName("chatId")]
        public string? ChatId { get; set; }
        [JsonPropertyName("date")]
        public string Date { get; set; }
        [JsonPropertyName("amount")]
        public double Amount { get; set; }
        [JsonPropertyName("description")]
        public string Description { get; set; }

        public TransactionSchema() {
            Id = ObjectId.GenerateNewId().ToString();
            Date = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
            Description = "";
        }
    }
}