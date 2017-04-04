import React, {Component} from "react";
import { connect } from 'react-redux';
import {PageHeader, Panel, Badge, Well} from 'react-bootstrap';
import * as actions from "../actions";


class BoxDetail extends Component {
  componentWillMount() {
    console.log('mounint -- ', this.props.boxTag);
    this.props.fetchBox(this.props.boxTag);
  }

  renderBoxDetails = () => {
    if (!this.props.box) {
      return <div>Loading...</div>
    }

    return (
      <div>
        <Badge>{this.props.box.pulls} pulls</Badge>
        <Panel header="Quick start">
          <Well bsSize="small">
            <p>vagrant init {this.props.boxTag} {window.location.origin}/{this.props.boxTag}</p>
            <p>vagrant up</p>
          </Well>
        </Panel>
        {!!this.props.box.short_description.length &&
          <Panel header="Short description">
            {this.props.box.short_description}
          </Panel>
        }
        {!!this.props.box.description.length &&
          <Panel header="Description">
            {this.props.box.description}
          </Panel>
        }
      </div>
    );
  };

  render() {
    console.log(this.props.box);
    return (
        <div>
          <PageHeader>{this.props.boxTag}</PageHeader>
          {this.renderBoxDetails()}
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  const {username, boxName} = props.params;
  const boxTag = `${username}/${boxName}`;
  return {
    box: state.entities.boxes[boxTag],
    boxTag,
  }
}

export default connect(mapStateToProps, {
  fetchBox: actions.loadBox,
})(BoxDetail)
