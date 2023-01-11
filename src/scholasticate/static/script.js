class Clock extends React.Component {
  constructor(props) {
    super(props);
    this.state = { date: new Date() };
  }

  tick() {
    this.setState({
      date: new Date()
    });
  }

  componentDidMount() {
    this.timerId = setInterval(
      () => this.tick(),
      500
    );
  }

  componentWillUnmount() {
    clearInterval(this.timerId);
  }

  render() {
    return (
      <div>
        <h1>Hello, from Scholasticate!</h1>
        <p>Current time: {this.state.date.toLocaleTimeString()}</p>
      </div>
    );
  }
}

ReactDOM.render(
  <Clock />,
  document.getElementById("reactRoot")
);