using api.Models;
using api.Services;
using Microsoft.AspNetCore.Mvc;

namespace api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class TransactionsController : ControllerBase
    {
        private readonly TransactionService _transactionService;

        public TransactionsController(TransactionService transactionService)
        {
            _transactionService = transactionService;
        }

        [HttpGet("{chatId}")]
        public ActionResult<List<Transaction>> GetTransactions(string chatId)
        {
            var transactions = _transactionService.Get(chatId);
            return Ok(transactions);
        }

        [HttpGet("{chatId}/{id}")]
        public ActionResult<Transaction> GetTransaction(string chatId, int id)
        {
            var transaction = _transactionService.Get(chatId, id);
            if (transaction == null)
                return NotFound();

            return Ok(transaction);
        }

        [HttpGet("{chatId}/history")]
        public ActionResult<History> GetHistory(string chatId)
        {
            var history = _transactionService.GetHistory(chatId);
            return Ok(history);
        }

        [HttpPost]
        public ActionResult<Transaction> CreateTransaction(Transaction transaction)
        {
            var createdTransaction = _transactionService.Create(transaction);
            return CreatedAtAction(nameof(GetTransaction), new { chatId = createdTransaction.ChatId, id = createdTransaction.Id }, createdTransaction);
        }

        [HttpPut("{chatId}/{id}")]
        public IActionResult UpdateTransaction(string chatId, int id, Transaction transaction)
        {
            _transactionService.Update(chatId, id, transaction);
            return NoContent();
        }

        [HttpDelete("{chatId}/{id}")]
        public IActionResult DeleteTransaction(string chatId, int id)
        {
            _transactionService.Remove(chatId, id);
            return NoContent();
        }
    }
}