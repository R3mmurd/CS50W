document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  document.querySelectorAll('button').forEach((button) => {
    button.addEventListener('click', () => {
      const messageContainer = document.querySelector('#message-container')
      messageContainer.className = '';
      messageContainer.innerHTML = '';
    })
  })

  document.querySelector('#compose-form').onsubmit = function() {
    send_email();
    return false;
  }

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#body-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#body-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  const emailsView = document.querySelector('#emails-view')
  emailsView.innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
      // Print emails
      console.log(emails);

      if (emails.length > 0) {
        let mailList = '<table class="table table-sm table-hover"><tbody>';

        emails.forEach(email => {
          const read = email.read ? 'read' : 'unread';
          mailList += `<tr class="email-row email-row-${read}" data-email-id="${email.id}">`;
          mailList += `<td class="col-from">${email.sender}</td>`;
          mailList += `<td class="col-subject">${email.subject}</td>`;
          mailList += `<td class="col-timestamp text-muted">${email.timestamp}</td>`;
          mailList += '</tr>';
        });
        
        mailList += '</tbody></table>'
        emailsView.innerHTML += mailList;

        document.querySelectorAll('.email-row').forEach((row) => {
          row.onclick = () => {
            loadEmail(row.dataset.emailId, mailbox);
          }
        });
      } else {
        emailsView.innerHTML += '<h5>Empty mailbox</h5>'
      }
  });
}

function send_email() {
    const recipients = document.querySelector('#compose-recipients').value;
    const subject = document.querySelector('#compose-subject').value;
    const body = document.querySelector('#compose-body').value;

    fetch('/emails', {
        method: 'POST',
        body: JSON.stringify({
            recipients: recipients,
            subject: subject,
            body: body
        })
    })
    .then(response => response.json())
    .then(result => {
      console.log(result);
      message = document.querySelector('#message-container')
      if ('error' in result) {
        message.className = "alert alert-danger"
        message.innerHTML = result['error']
      } else {
        message.className = "alert alert-success"
        message.innerHTML = result['message']
        load_mailbox('sent')
      }
    })
    .catch(() => {
        console.error('Error')
    });
}

function loadEmail(emailId, mailbox) {
  fetch(`/emails/${emailId}`)
  .then(response => response.json())
  .then(email => {
      // Print email
      console.log(email);

      if ('error' in email) {
        message = document.querySelector('#message-container')
        message.className = "alert alert-danger"
        message.innerHTML = email['error']
      } else {
        header = `<strong>From:</strong> ${email.sender}<br>`;
        header += `<strong>To:</strong> ${email.recipients.join(', ')}<br>`;
        header += `<strong>Subject:</strong> ${email.subject}<br>`;
        header += `<strong>Timestamp:</strong> ${email.timestamp}<br>`;
        header += `<button class="btn btn-sm btn-outline-primary" id="reply">Reply</button>`

        if (mailbox === 'inbox') {
          header += `<button class="btn btn-sm btn-outline-primary" id="toggle-archived">Archive</button>`;
        } else if (mailbox === 'archive') {
          header += `<button class="btn btn-sm btn-outline-primary" id="toggle-archived">Unarchive</button>`;
        }

        document.querySelector('#emails-view').innerHTML = header;

        buttonToggleArchived = document.querySelector('#toggle-archived');

        if (buttonToggleArchived) {
          buttonToggleArchived.onclick = () => { toggleArchived(email); };
        }

        document.querySelector('#reply').onclick = () => { reply(email); };

        document.querySelector('#body-view').innerHTML = '<hr>' + email.body
        document.querySelector('#body-view').style.display = 'block';

        if (!email.read) {
          fetch(`/emails/${emailId}`,{
            method: 'PUT',
            body: JSON.stringify({
              read: true
            })
          });
        }
      }
  });
}

function toggleArchived(email) {
  const archived = !email.archived;
  fetch(`/emails/${email.id}`,{
    method: 'PUT',
    body: JSON.stringify({
      archived: archived
    })
  })
  .then(() => {
    const messageContainer = document.querySelector('#message-container')
    messageContainer.className = 'alert alert-success';
    if (archived) {
      messageContainer.innerHTML = 'Email archived successfully.';
    } else {
      messageContainer.innerHTML = 'Email unarchived successfully.';
    }
    load_mailbox('inbox');
  });
}

function reply(email) {
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#body-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  subject = email.subject;

  if (!subject.startsWith('Re:')) {
    subject = `Re: ${subject}`;
  }

  document.querySelector('#compose-recipients').value = email.sender;
  document.querySelector('#compose-subject').value = subject
  document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote: ${email.body}\n\n`;
  document.querySelector('#compose-body').focus();
}