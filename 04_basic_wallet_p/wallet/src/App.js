import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
    const server = 'http://localhost:5000'
    const [lastUsername, setLastUsername] = useState('user')
    const [username, setUsername] = useState('user')
    const [balance, setBalance] = useState(0)
    const [isMining, setIsMining] = useState(false)
    const [transactions, setTransactions] = useState([])

    useEffect(() => {
        axios.post(`${server}/user/balance`, { 'username': lastUsername }).then(res => {
            console.log('/user/balance', res.data.balance)
            setBalance(res.data.balance)
        }).catch(err => console.error(err));
        axios.post(`${server}/user/transactions`, { 'username': lastUsername }).then(res => {
            console.log('/user/transactions', res.data.transactions)
            setTransactions(res.data.transactions)
        }).catch(err => console.error(err));
    }, [])

    const onChangeUsername = (e) => {
        const { value } = e.target;
        setUsername(value)
    }

    const onChangeUsernameSubmit = (e) => {
        e.preventDefault();
        axios.post(`${server}/user/change`, { lastUsername, username }).then(res => {
            console.log('/user/change', res)
            if (res.data.success) {
                setTransactions(prevState => prevState.map(t => {
                    if (t.sender === lastUsername) {
                        t.sender = username
                    }
                    if (t.recipient === lastUsername) {
                        t.recipient = username
                    }
                    return t
                }))
                setLastUsername(username)
            }
        }).catch(err => console.error(err));
    }

    const onClickStartMine = (e) => {
        if (!isMining) {
            setIsMining(true)
            axios.post(`${server}/mine`, {
                'username': lastUsername
            }).then(res => {
                console.log('/mine', res.data)
                const myTransactions = res.data.transactions.filter(t => t.sender === lastUsername || t.recipient === lastUsername)
                setTransactions(prevState => [
                    ...prevState,
                    ...myTransactions
                ]);
                setBalance(prevState => prevState + myTransactions.reduce((total, t) => {
                    if (t.sender === lastUsername) {
                        total -= t.amount
                    } else if (t.recipient === lastUsername) {
                        total += t.amount
                    }
                    return total
                }, 0));
            }).catch(err => {
                console.error(err)
            }).finally(e => {
                setIsMining(false)
            });
        }
    }

    return (
        <div className="App">
            <h2>{lastUsername}'s balance: {balance} Coins</h2>
            <form onSubmit={onChangeUsernameSubmit}>
                <label htmlFor="username">User name:</label>
                <input id="username" type="text" value={username} onChange={onChangeUsername} />
                <button>Change now</button>
            </form>
            {
                !isMining ? <>
                    <button onClick={onClickStartMine}>Start Mining</button>
                </> : <>
                        <h2>Mining...</h2>
                    </>
            }
            {
                transactions.map((t, i) => <div key={i}>
                    <p>Sender: {t.sender}</p>
                    <p>Recipient: {t.recipient}</p>
                    <p>Amount: {t.amount}</p>
                </div>)
            }
        </div>
    );
}

export default App;