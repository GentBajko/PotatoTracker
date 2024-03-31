namespace api.Models
{
    public class Transaction
    {
        public int Id { get; set; }
        public string? ChatId { get; set; }
        public DateTime Date { get; set; }
        public TransactionType Type { get; set; }
        public string? Description { get; set; }
    }
}