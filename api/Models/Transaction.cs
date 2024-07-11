namespace api.Models
{
    public class Transaction
    {
        public MongoDB.Bson.ObjectId Id { get; set; }
        public string? ChatId { get; set; }
        public decimal Amount { get; set; }
        public DateTime Date { get; set; }
        public TransactionType Type { get; set; }
        public string? Description { get; set; }
    }
}