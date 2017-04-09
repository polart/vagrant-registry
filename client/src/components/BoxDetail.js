import React, {Component} from "react";
import { connect } from 'react-redux';
import {PageHeader, Panel, Badge, Well, Tabs, Tab} from 'react-bootstrap';
import * as actions from "../actions";
import BoxVersionList from "./BoxVersionList";
import MyBreadcrumbs from "./MyBreadcrumbs";


class BoxDetail extends Component {
  componentWillMount() {
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
          <MyBreadcrumbs router={this.props.router} />
          <Tabs id="box-tabs">
            <Tab eventKey={1} title="Box Info">
              {this.renderBoxDetails()}
            </Tab>
            <Tab eventKey={2} title="Versions">
              <BoxVersionList boxTag={this.props.boxTag} router={this.props.router} />
            </Tab>
          </Tabs>
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
